import json
import logging
import os
import datetime

import boto3

from utils import parse_log_lines
from auth import check_auth
from logger import log

config = {
    "DYNAMODB_REGION": os.environ["DYNAMODB_REGION"],
    "DYNAMODB_TABLE_NAME": os.environ["DYNAMODB_TABLE_NAME"],
    "KINESIS_BATCH_SIZE": os.environ.get("KINESIS_BATCH_SIZE", 500),
    "KINESIS_REGION": os.environ["KINESIS_REGION"],
    "KINESIS_STREAM_NAME": os.environ["KINESIS_STREAM_NAME"],
}


def lambda_handler(event, context):
    log.debug("Received event: " + json.dumps(event))
    check_auth(event["headers"], config)
    handle_lambda_proxy_event(event)
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Length": 0},
    }


def handle_lambda_proxy_event(event):
    headers = event["headers"]

    body = event["body"]

    # TODO: Move out of handler.
    assert headers["X-Forwarded-Proto"] == "https"
    assert headers["Content-Type"] == "application/logplex-1"

    loglines = parse_log_lines(body)
    put_loglines_to_kinesis(loglines)

    if log.isEnabledFor(logging.DEBUG):
        for evt in loglines:
            log.debug("Event: %s", evt)
            log.debug("Message: %s", evt["message"])

    if log.isEnabledFor(logging.DEBUG):
        log.debug(
            "Header counter: %d | Parser count: %d",
            int(headers["Logplex-Msg-Count"]),
            len(loglines),
        )
        assert int(headers["Logplex-Msg-Count"]) == len(loglines)

    return ""


def serializer(o):
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()


def put_loglines_to_kinesis(loglines):
    kinesisClient = boto3.client("kinesis", region_name=config["KINESIS_REGION"])
    records = []

    if log.isEnabledFor(logging.DEBUG):
        log.debug(
            "Sending %d records to kinesis stream %s",
            len(loglines),
            config["KINESIS_STREAM_NAME"],
        )

    for line in loglines:
        records.append(
            {"Data": json.dumps(line, default=serializer), "PartitionKey": "key"}
        )
        if len(records) and len(records) % config["KINESIS_BATCH_SIZE"] == 0:
            put_records(kinesisClient, records)
            records = []

    if len(records):
        put_records(kinesisClient, records)


def put_records(kclient, records):
    resp = kclient.put_records(
        Records=records, StreamName=config["KINESIS_STREAM_NAME"]
    )
    if resp["FailedRecordCount"]:
        log.warn(
            "PutRecords call with %d records had a failure count of %d",
            len(records),
            resp["FailedRecordCount"],
        )
