# noinspection PyUnusedImports
import pytest
import zmq
from Calendar import *
import config

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(f"tcp://localhost:{config.PORT}")

TEST_DATES = [
    "2026-03-12T16:00:00Z",
    "1950-05-05T12:00:00Z",
    "2030-03-30T16:00:00Z",
    "2012-01-01T16:00:00Z"
]

TEST_ITEMS = [
    {"date_time": TEST_DATES[0], "data": "Test data 1"},
    {"date_time": TEST_DATES[1], "data": ["Test data 2a", "Test data 2b"]},
    {"date_time": TEST_DATES[2], "data": 3},
    {"date_time": TEST_DATES[0], "data": {"key1": "test data 4a", "key2": "test data4b"}}
]

def test_listen():
    """ Testing that service replies at all """
    socket.send_json({
        "action": "test",
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    response = socket.recv_json()
    assert response["status"] == "error"

def test_parse_req_bad_key():
    """ Send a request with one of the keys missing"""
    socket.send_json({
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    response = socket.recv_json()
    assert response["status"] == STATUS_ERROR and response["data"] == ERR_REQ_MISSING_KEY

def test_parse_req_bad_timestamp():
    socket.send_json({
        "action": Actions.SEL_EXACT,
        "start_date": "2026-03-12 4:00pm",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    response = socket.recv_json()
    assert response["status"] == STATUS_ERROR and response["data"] == ERR_BAD_TIMESTAMP

# TODO
def test_item_bad_key():
    pass

# TODO
def test_parse_item_bad_timestamp():
    pass

def test_parse_select_exact_no_count():
    socket.send_json({
        "action": Actions.SEL_EXACT,
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": TEST_ITEMS
    })

    response = socket.recv_json()
    assert response["status"] == STATUS_SUCCESS and response["data"] == ERR_REQ_MISSING_KEY

# TODO
def test_parse_select_exact_count():
    pass

# TODO
def test_parse_select_range_no_count():
    pass

# TODO
def test_parse_select_range_count():
    pass

# TODO
def test_parse_select_after_no_count():
    pass

# TODO
def test_parse_select_after_count():
    pass

# TODO
def test_parse_select_before_no_count():
    pass

# TODO
def test_parse_select_before_count():
    pass

# TODO
def test_parse_select_daily_no_count():
    pass

# TODO
def test_parse_select_weekly_count():
    pass

# TODO
def test_parse_select_monthly_no_count():
    pass

# TODO
def test_parse_select_monthly_count():
    pass

# TODO
def test_parse_select_yearly_no_count():
    pass

# TODO
def test_parse_select_yearly_count():
    pass

# TODO
def test_selects_no_items():
    req = {
        "action": Actions.SEL_EXACT,
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    }
    socket.send_json(req)
    rep = socket.recv_json()
    assert False # Todo

    req.action = Actions.SEL_RANGE
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_AFTER
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_BEFORE
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_DAILY
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_WEEKLY
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_MONTHLY
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo

    req.action = Actions.SEL_YEARLY
    socket.send_json(req)
    rep = socket.recv_json()
    assert False  # Todo
