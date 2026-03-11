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
    req = socket.recv_json()
    parsed_req = parse_request(req)

    rep = process_request(parsed_req)
    socket.send_json(rep)



def parse_request(raw_req) -> Request:
    pass


def process_request(req: Request) -> dict:
    match req.type:
        case "select exact":
            result = get_items_exact(req)
        case "select range" | "select after" | "select before":
            result = get_items_in_range(req)
        case "select daily range":
            pass
        case "select monthly range":
            pass
        case "select yearly range":
            pass
        case _:
            pass
    pass


def get_items_exact(req: Request) -> list:
    """ Returns the items whose datetime matches the request's exactly """
    pass

def get_items_in_range(req: Request) -> list:
    """ Returns the items whose datetime is within (inclusive) the given
        range. """
    pass

def get_items_in_daily_range(req: Request) -> list:
    """ Returns the items whose datetime is within a given range of time during
        the day, such as items between 6pm and 8pm. """
    pass

def get_items_in_weekly_range(req: Request) -> list:
    """ Returns the items whose datetime is within a given range during a week,
        such as items on Fridays and Saturdays. """
    pass

def get_items_in_monthly_range(req: Request) -> list:
    """ Returns items whose datetime is within a given range during a month,
        such as items on the 1st of the months, or during the 2nd weeks. """
    pass

def get_items_in_yearly_range(req: Request) -> list:
    """ Returns items whose datetime is within a given range during a year,
        such as items in the summers. """
    pass

def get_items_in_interval(req: Request) -> list:
    """ Returns items within the given range relative to an interval, such as
        items from 12pm to 1pm on every 3rd day."""
    pass

if __name__ == "__main__":
    main()