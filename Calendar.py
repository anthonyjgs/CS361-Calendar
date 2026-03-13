import zmq
import datetime as dt


PORT = 414635

class Request:
    """ The essential data to process calendar requests """
    type: str
    start_date: dt.datetime
    end_date: dt.datetime
    count: int
    items: list

def main():
    print("Calendar Service")
    print("Initializing...")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://localhost:{PORT}")
    print(f"Listening on port {PORT}")

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
        reply = {"status": "error", "data": error}
    else:
        reply = process_request(parsed_req)

    socket.send_json(reply)


def parse_request(raw_req) -> tuple[Request, str]:
    """ Parses the request and returns the parsed request. Returns an error
        string as well if something goes wrong. """
    error_str = None
    request = Request()

    # Fill the request object with the parsed values, returning an error string
    # describing any failures
    try:
        request.type = raw_req["type"]
        request.count = int(raw_req["count"])
        request.items = raw_req["items"]

        # Parse iso timestamps into datetime objects
        try:
            request.start_date = dt.datetime.fromisoformat(raw_req["start_date"])
            request.end_date = dt.datetime.fromisoformat(raw_req["end_date"])
        except ValueError as e:
            print(f"Error during parsing: {e}")
            request.type = "error"
            error_str = "bad iso timestamp"

    except KeyError as e:
        print(f"Error during parsing: {e}")
        request.type = "error"
        error_str = "data is missing one of the key-value pairs"

    return request, error_str


def process_request(req: Request) -> dict:
    """ Proceses the request based on its 'type' field, returning a dict with
        the result's status and data """
    status = "success"
    
    match (req.type):
        case "select exact":
            result = get_items_exact(req)
        case "select range" | "select after" | "select before":
            result = get_items_in_range(req)
        case "select daily range":
            result = get_items_in_daily_range(req)
        case "select monthly range":
            result = get_items_in_monthly_range(req)
        case "select yearly range":
            result = get_items_in_yearly_range(req)
        case _:
            status = "error"
            result = f"Unknown request type: {req.type}"

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