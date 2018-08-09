def filter_log_lines(msg):
    """Return true if we should send to kinesis."""
    if "DEBUG" in msg:
        return False

    return True


def parse_rfc6587(payload):
    loglines = []
    while payload:
        msg_len, syslog_msg_payload = payload.split(" ", maxsplit=1)
        msg_len = int(msg_len)

        # The msg_len is a bytes len, so we convert to bytes for the slicing step
        syslog_msg_payload = syslog_msg_payload.encode("utf-8")

        syslog_msg = syslog_msg_payload[0:msg_len].decode("utf-8")
        payload = syslog_msg_payload[msg_len:].decode("utf-8")

        loglines.append(syslog_msg)
    return loglines
