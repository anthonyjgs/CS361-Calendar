import zmq
import datetime as dt
import config

# Request actions
class Actions:
    SEL_EXACT = "select exact"
    SEL_RANGE = "select range"
    SEL_AFTER = "select after"
    SEL_BEFORE = "select before"
    SEL_DAILY = "select daily range"
    SEL_MONTHLY = "select monthly range"
    SEL_YEARLY = "select yearly range"

# Response Statuses
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# Response Error Strings
ERR_REQ_MISSING_KEY = "request is missing a key-value(s)"
ERR_ITEM_MISSING_KEY = "item is missing a key-value(s)"
ERR_REQ_BAD_TIMESTAMP = "start or end date has invalid iso timestamp"
ERR_ITEM_BAD_TIMESTAMP = "item has invalid iso timestamp"
ERR_UNKNOWN_ACTION = "unknown action"


class Item:
    date_time: dt.datetime
    data = None

class Request:
    """ The essential data to process calendar requests """
    action: str
    start_date: dt.datetime
    end_date: dt.datetime
    count: int|None
    items: list

def main():
    print("Calendar Service")
    print("Initializing...")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://localhost:{config.PORT}")
    print(f"Listening on port {config.PORT}")

    try:
        while True:
            service_listen(socket)
    except KeyboardInterrupt:
        print("Shutting down...")
        socket.close()


def service_listen(socket: zmq.Socket) -> None:
    """ Listen and process one request """
    req = socket.recv_json()

    parsed_req, error = parse_request(req)

    if error is not None:
        reply = {"status": STATUS_ERROR, "data": error}
    else:
        reply = process_request(parsed_req)

    socket.send_json(reply)


def parse_request(raw_req) -> tuple[Request, str|None]:
    """ Parses the request and returns the parsed request. Returns an error
        string as well if something goes wrong. """
    error_str = None
    request = Request()

    # Fill the request object with the parsed values, returning an error string
    # describing any failures
    try:
        request.action = raw_req["action"]

        request.items, error_str = parse_items(raw_req["items"])
        if error_str is not None:
            return request, error_str

        if raw_req["count"] is not None:
            request.count = int(raw_req["count"])
        else:
            request.count = None

        # Parse iso timestamps into datetime objects
        try:
            request.start_date = dt.datetime.fromisoformat(raw_req["start_date"])
            request.end_date = dt.datetime.fromisoformat(raw_req["end_date"])

        except ValueError as e:
            print(f"ValueError during parsing: {e}")
            error_str = ERR_REQ_BAD_TIMESTAMP
    except KeyError as e:
        print(f"KeyError during request parsing: {e}")
        error_str = ERR_REQ_MISSING_KEY

    return request, error_str

def parse_items(raw_items) -> tuple[list, str|None]:
    """ Parses one item from the json dict into an item object """
    error_str = None
    parsed_items = []
    for raw_item in raw_items:
        parsed_item = Item()
        try:
            parsed_item.date = dt.datetime.fromisoformat(raw_item["date_time"])
            parsed_item.data = raw_item["data"]
            parsed_items.append(parsed_item)

        except KeyError as e:
            print(f"KeyError during item parsing: {e}")
            error_str = ERR_ITEM_MISSING_KEY
            return parsed_items, error_str
        except ValueError as e:
            print(f"ValueError during item parsing: {e}")
            error_str = ERR_ITEM_MISSING_KEY
            return parsed_items, error_str

    return parsed_items, error_str


def process_request(req: Request) -> dict:
    """ Proceses the request based on its 'action' field, returning a dict with
        the result's status and data """
    status = "success"
    
    match req.action:
        case Actions.SEL_EXACT:
            result = get_items_exact(req)
        case Actions.SEL_RANGE | Actions.SEL_AFTER | Actions.SEL_BEFORE:
            result = get_items_in_range(req)
        case Actions.SEL_DAILY:
            result = get_items_in_daily_range(req)
        case Actions.SEL_MONTHLY:
            result = get_items_in_monthly_range(req)
        case Actions.SEL_YEARLY:
            result = get_items_in_yearly_range(req)

        case _:
            status = "error"
            result = f"{ERR_UNKNOWN_ACTION}: {req.action}"

    return {"status": status, "data": result}


def get_items_exact(req: Request) -> list:
    """ Returns the items whose datetime matches the request's exactly """
    return [item for item in req.items if item.date == req.start_date]

def get_items_in_range(req: Request) -> list:
    """ Returns the items whose datetime is within (inclusive) the given
        range. """
    return [item for item in req.items if (req.start_date <= item.date <= req.end_date)]

def get_items_in_daily_range(req: Request) -> list:
    """ Returns the items whose datetime is within a given range of time during
        the day, such as items between 6pm and 8pm. """
    matches = []

    for item in req.items:
        item_time = item.datetime.time()
        if req.start_date.time() <= item_time <= req.end_date.time():
            matches.append(item)

    return matches

def get_items_in_weekly_range(req: Request) -> list:
    """ Returns the items whose datetime is within a given range during a week,
        such as items on Fridays and Saturdays. """
    matches = []
    start_day = req.start_date.weekday()
    end_day = req.end_date.weekday()

    for item in req.items:
        item_day = item.datetime.weekday()
        if start_day <= item_day <= end_day:
            matches.append(item)

    return matches

def get_items_in_monthly_range(req: Request) -> list:
    """ Returns items whose datetime is within a given range during a month,
        such as items on the 1st of the months, or during the 2nd weeks. """
    matches = []

    for item in req.items:
        if req.start_date.day <= item.datetime.day <= req.end_date.day:
            matches.append(item)

    return matches

def get_items_in_yearly_range(req: Request) -> list:
    """ Returns items whose datetime is within a given range during a year,
        such as items in the summers. """
    matches = []

    normalized_start = req.start_date.replace(year=1)
    normalized_end = req.end_date.replace(year=1)
    for item in req.items:
        normalized_item = item.datetime.replace(year=1)
        if normalized_start <= normalized_item <= normalized_end:
            matches.append(item)

    return matches

if __name__ == "__main__":
    main()