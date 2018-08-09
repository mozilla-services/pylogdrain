# Lambda Function for ingesting syslog-over-https

This lambda function ingests syslog-over-https with basic auth, specifically targetting Heroku
logdrains.

It uses a JSON document stored in S3 to store username/password combinations, with the password being
bcrypt hashed. After authenticating a request, it will send the logs to a Kinesis stream, one log line per record.

Additionally, this lambda function requires an API Gateway in front of it.

## Deployment

TODO

#### Auth JSON document

##### S3 Configuration

As you will see in the cloudformation examples, it is suggested that you turn on
[Versioning](https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html) on the S3
bucket you use to store the authentication document.

### Environment Variables

#### AUTH_S3_BUCKET (required)

The S3 bucket that holds the authentication json document.

Example: `AUTH_S3_BUCKET='pylogdrain-auth-storage'`

#### AUTH_S3 (required)

The key to the authentication json document stored in the `AUTH_S3_BUCKET` bucket.

Example: `AUTH_S3_KEY='auth.json'`

#### AUTH_S3_REGION (required)

The region that the S3 bucket is in.

Example: `AUTH_S3_REGION="us-west-2"`

#### KINESIS_STREAM_NAME (required)

The name of the Kinesis stream that Cloudtrail records will be pushed to.

Example: `KINESIS_STREAM_NAME="pylogdrain"`

#### KINESIS_REGION (required)

The region that the Kinesis stream lives in.

Example: `KINESIS_REGION="us-west-2"`

#### KINESIS_BATCH_SIZE (optional)

The number of records in a batched put to the Kinesis stream.

By default, `KINESIS_BATCH_SIZE` is set to `500` (which is the max allowed).

#### LOGLEVEL (optional)

Log level to use, where the options are "DEBUG", "INFO", or "WARN".

By default, `LOGLEVEL` is set to "INFO".
