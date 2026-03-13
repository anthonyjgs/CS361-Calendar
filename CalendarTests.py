from urllib import response

# noinspection PyUnusedImports

import pytest
import zmq
from Calendar import *
import config

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(f"tcp://localhost:{config.PORT}")

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

def test_parse_bad_key():
    """ Send a request with one of the keys missing"""
    socket.send_json({
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    response = socket.recv_json()
    assert response["status"] == STATUS_ERROR and response["data"] == ERR_REQ_MISSING_KEY

def test_parse_bad_timestamp():
    socket.send_json({
        "action": Actions.SEL_EXACT,
        "start_date": "2026-03-12 4:00pm",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    response = socket.recv_json()
    assert response["status"] == STATUS_ERROR and response["data"] == ERR_BAD_TIMESTAMP

def test_parse_select_exact():
    socket.send_json({
        "action": Actions.SEL_EXACT,
        "start_date": "2026-03-12T16:00:00Z",
        "end_date": "2026-03-12T16:00:00Z",
        "count": None,
        "items": None
    })

    resposne = socket.recv_json()
    assert response["status"] == STATUS_SUCCESS and response["data"] == ERR_REQ_MISSING_KEY