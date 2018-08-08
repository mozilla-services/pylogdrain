from ..utils import Parser


LOGLINES = [
    [
        (
            "142 <172>1 2018-08-03T20:54:53+00:00 host heroku logplex - Error L10 (output"
            " buffer overflow): 7 messages dropped since 2018-08-03T19:11:37+00:00.249 <158>"
            "1 2018-08-03T20:54:51.892800+00:00 host heroku router - at=info method=GET path"
            '="/favicon.ico" host=tester request_id=f1c793a4-d939'
            '-47f0-a2e1-26a1df1012a8 fwd="256.0.0.10" dyno=web.1 connect=1ms service='
            "1ms status=404 bytes=146 protocol=https\n"
        ),
        {"len": 2, "startswith": "Error", "endswith": "https"},
    ],
    [
        (
            "63 <190>1 2018-08-03T20:54:50.727857+00:00 host app web.1 - Hit /\n"
            "69 <190>1 2018-08-03T20:54:50.727989+00:00 host app web.1 - My message \n"
            "64 <190>1 2018-08-03T20:54:50.727991+00:00 host app web.1 -  with \n"
            "69 <190>1 2018-08-03T20:54:50.727993+00:00 host app web.1 -  new lines \n"
            "67 <190>1 2018-08-03T20:54:50.727994+00:00 host app web.1 -  and such\n"
            "124 <190>1 2018-08-03T20:54:50.728828+00:00 host app web.1 - "
            "[GIN] 2018/08/03 - 20:54:50 | 200 | 986.188µs | 256.0.0.10 | GET /\n"
            "140 <190>1 2018-08-03T20:54:50.891609+00:00 host app web.1 - "
            "[GIN] 2018/08/03 - 20:54:50 | 200 | 132.298µs | 256.0.0.10 | "
            "GET /static/main.css\n"
        ),
        {"len": 7, "startswith": "Hit /", "endswith": "main.css"},
    ],
    [
        (
            "247 <158>1 2018-08-03T22:38:42.839569+00:00 host heroku router"
            ' - at=info method=GET path="/favicon.ico" host=tester request_'
            'id=189b83b2-e440-4d09-a760-5940f26740ab fwd="256.0.0.10" dyno='
            "web.1 connect=1ms service=1ms status=404 bytes=146 protocol=https\n"
            "154 <190>1 2018-08-03T22:38:42.975461+00:00 host app web.1 - ["
            "GIN] 2018/08/03 - 22:38:42 | 200 |     170.221µs |  256.0.0.10"
            " | GET      /static/lang-logo.png\n"
            "146 <190>1 2018-08-03T22:38:43.087424+00:00 host app web.1 - ["
            "GIN] 2018/08/03 - 22:38:43 | 404 |       1.973µs |  256.0.0.10"
            " | GET      /favicon.ico\n"
        ),
        {"len": 3, "startswith": "at=info", "endswith": "favicon.ico"},
    ],
]


def test_parse():
    parser = Parser()
    logline = (
        '<158>1 2018-08-03T22:38:42.839569+00:00 host heroku router - at=info'
        ' method=GET path="/favicon.ico" host=tester request_id=189b83b2-e440'
        '-4d09-a760-555555555555 fwd="256.111.155.10" dyno=web.1 connect=1ms '
        'service=1ms status=404 bytes=146 protocol=https'
    )
    results = parser.parse(logline)

    assert results["priority"] == 158
    assert results["severity"] == 6
    assert results["facility"] == 19
    assert results["version"] == "1"
    assert results["timestamp"].year == 2018
    assert results["hostname"] == "host"
    assert results["source"] == "heroku"
    assert results["appname"] == "router"
    assert "host=tester" in results["message"]


def test_parse_rfc6587():
    parser = Parser()
    for line in LOGLINES:
        results = parser.parse_rfc6587(line[0])
        assert len(results) == line[1]["len"]
        assert results[0]['message'].startswith(line[1]['startswith'])
        assert results[-1]['message'].endswith(line[1]['endswith'])
