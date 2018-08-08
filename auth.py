import json
import logging

from base64 import b64decode
from urllib.parse import unquote

import boto3
from bcrypt import checkpw

from logger import log


class AuthenticationError(Exception):
    pass


class BasicAuthDecodeError(Exception):
    pass


class BasicAuthHandler(object):
    def __init__(self, config):
        self.dynamo_region = config["DYNAMODB_REGION"]
        self.dynamo_client = boto3.client("dynamodb", region_name=self.dynamo_region)
        self.dynamo_table = config["DYNAMODB_TABLE_NAME"]

    def check_header(self, basicauth_header):
        """
        Checks Basic Auth header value against username/password combos
        in dynamodb.

        Returns True if it finds a match, else it returns False.
        """
        try:
            username, password = self.decode(basicauth_header)
        except BasicAuthDecodeError:
            return False

        resp = self.dynamo_client.get_item(
            TableName=self.dynamo_table, Key={"username": {"S": username}}
        )

        if log.isEnabledFor(logging.DEBUG):
            log.debug("Resp from Dynamo: " + json.dumps(resp))

        if "Item" in resp and checkpw(
            password.encode("utf-8"), resp["Item"]["password"]["S"].encode("utf-8")
        ):
            return True

        return False

    # Taken from https://github.com/rdegges/python-basicauth
    def decode(self, basicauth_header):
        """
        Decode an encrypted HTTP basic authentication string.

        Returns a tuple of the form (username, password), and
        raises a BasicAuthDecodeError exception if nothing could be decoded.
        """
        split = basicauth_header.strip().split(" ")

        # If split is only one element, try to decode the username and password
        # directly.
        if len(split) == 1:
            try:
                username, password = b64decode(split[0]).decode().split(":", 1)
            except:
                raise BasicAuthDecodeError

        # If there are only two elements, check the first and ensure it says
        # 'basic' so that we know we're about to decode the right thing. If not,
        # bail out.
        elif len(split) == 2:
            if split[0].strip().lower() == "basic":
                try:
                    username, password = b64decode(split[1]).decode().split(":", 1)
                except:
                    raise BasicAuthDecodeError
            else:
                raise BasicAuthDecodeError

        else:
            raise BasicAuthDecodeError

        return unquote(username), unquote(password)


def check_auth(headers, config):
    if "Authorization" not in headers:
        msg = "'Authorization' header not found in headers, exiting"
        log.error(msg)
        raise AuthenticationError(msg)

    ba_handler = BasicAuthHandler(config)
    if not ba_handler.check_header(headers["Authorization"]):
        msg = (
            "username/password combo in 'Authorization' header was not found in DynamoDB table %s, exiting"
            % config["DYNAMODB_TABLE_NAME"]
        )
        log.error(msg)
        raise AuthenticationError(msg)

    return True
