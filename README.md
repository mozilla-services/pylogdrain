# Lambda Function for ingesting syslog-over-https

This lambda function ingests syslog-over-https with basic auth, specifically targetting Heroku
logdrains.

It uses a DynamoDB table to store username/password combinations, with the password being
bcrypt hashed. After validating that a request has a working use of credentials, it will
send the logs to a Kinesis stream, one log line per record.

Additionally, this lambda function requires an API Gateway in front of it.

## Deployment

TODO

### Environment Variables

#### DYNAMODB_TABLE_NAME (required)

The name of the DynamoDB table that contains authentication records.

Example: `DYNAMODB_TABLE_NAME="pylogdrain-auth"`

#### DYNAMODB_REGION (required)

The region that the DynamoDB table lives in.

Example: `DYNAMODB_REGION="us-west-2"`

#### KINESIS_STREAM_NAME (required)

The name of the Kinesis stream that Cloudtrail records will be pushed to.

Example: `KINESIS_STREAM_NAME="pylogdrain"`

#### KINESIS_REGION (required)

The region that the Kinesis stream lives in.

Example: `KINESIS_REGION="us-west-2"`

#### KINESIS_BATCH_SIZE (optional)

The number of records in a batched put to the Kinesis stream.

By default, `KINESIS_BATCH_SIZE` is set to `500` (which is the max allowed).

## References

The parsing code and structure of this project is based off of this tutorial:
https://spiegelmock.com/2017/10/26/heroku-logging-to-aws-lambda/
