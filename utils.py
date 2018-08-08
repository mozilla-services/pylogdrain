from syslog import LOG_DEBUG

import iso8601
from pyparsing import Word, Suppress, nums, Optional, Regex, pyparsing_common, alphanums


def parse_log_lines(body):
    parser = Parser()
    return [l for l in parser.parse_rfc6587(body) if filter_log_lines(l)]


def filter_log_lines(msg):
    """Return true if we should send to kinesis."""
    sev = msg["severity"]  # e.g. LOG_DEBUG
    body = msg["message"]

    if sev >= LOG_DEBUG:
        return False

    if body.startswith("DEBUG   "):
        return False

    return True


class Parser(object):
    def __init__(self):
        ints = Word(nums)

        # priority
        priority = Suppress("<") + ints + Suppress(">")

        # version
        version = ints

        # timestamp
        timestamp = pyparsing_common.iso8601_datetime

        # hostname
        hostname = Word(alphanums + "_" + "-" + ".")

        # source
        source = Word(alphanums + "_" + "-" + ".")

        # appname
        appname = (
            Word(alphanums + "(" + ")" + "/" + "-" + "_" + ".")
            + Optional(Suppress("[") + ints + Suppress("]"))
            + Suppress("-")
        )

        # message
        message = Regex(".*")

        # pattern build
        self.__pattern = (
            priority + version + timestamp + hostname + source + appname + message
        )

    def get_chunk(self, payload):
        msg_len, syslog_msg_payload = payload.split(" ", maxsplit=1)
        msg_len = int(msg_len)

        # TODO: This is a fun one, and this fix is very hacky and will not work if the log line has enough
        #       unicode characters to push far enough into the next line that also has unicode characters.
        # This fixes a problem where the message length counts all unicode characters a 2 characters.
        # Would probably be a lot better to decode into ascii safely and properly
        num_of_unicode_chars = len(
            [c for c in syslog_msg_payload[0:msg_len] if ord(c) > 128]
        )
        msg_len -= num_of_unicode_chars

        # only grab msg_len bytes of syslog_msg
        syslog_msg = syslog_msg_payload[0:msg_len]
        next_payload = syslog_msg_payload[msg_len:]

        yield syslog_msg

        if next_payload:
            yield from self.get_chunk(next_payload)

    def parse_rfc6587(self, payload):
        """
        Splits up batched syslog messages and parses them. Returns a list of parsed syslog messages.
        """
        return [self.parse(line) for line in self.get_chunk(payload)]

    def parse(self, line):
        parsed = self.__pattern.parseString(line)

        # https://tools.ietf.org/html/rfc5424#section-6
        # get priority/severity
        priority = int(parsed[0])
        severity = priority & 0x07
        facility = priority >> 3

        payload = {}
        payload["priority"] = priority
        payload["severity"] = severity
        payload["facility"] = facility
        payload["version"] = parsed[1]
        payload["timestamp"] = iso8601.parse_date(parsed[2])
        payload["hostname"] = parsed[3]
        payload["source"] = parsed[4]
        payload["appname"] = parsed[5]
        payload["message"] = parsed[6]

        return payload
