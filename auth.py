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
        self.s3_client = boto3.client("s3", region_name=config["AUTH_S3_REGION"])
        self.s3_bucket = config["AUTH_S3_BUCKET"]
        self.s3_key = config["AUTH_S3_KEY"]

    def get_auth_json_from_s3(self):
        resp = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.s3_key)
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Resp from S3: %s", resp)
        return json.loads(resp['Body'].read())

    def get_password(self, username):
        auth_json = self.get_auth_json_from_s3()
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Iterating through %d credentials", len(auth_json))
        for creds in auth_json:
            if creds['username'] == username:
                return creds['password']
        return None

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

        stored_password = self.get_password(username)
        if stored_password is None:
            return False

        if checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
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
