import selectors
import socket
from typing import Iterable, Optional, NamedTuple


class Addr(NamedTuple):
    host: str
    port: int


class Poller:
    def __init__(self) -> None:
        self.selector = selectors.DefaultSelector()

    def register(self, conn: socket.socket) -> None:
        self.selector.register(conn, selectors.EVENT_READ, data=None)

    def unregister(self, conn: socket.socket) -> None:
        self.selector.unregister(conn)

    def poll(self, timeout: Optional[float] = None) -> Iterable[socket.socket]:
        events = self.selector.select(timeout=timeout)
        return (
            key.fileobj
            for key, mask in events
            if mask & selectors.EVENT_READ and isinstance(key.fileobj, socket.socket)
        )


if __name__ == "__main__":
    poller = Poller()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_addr = "localhost", 7003

    s.bind(host_addr)
    s.listen()

    s.setblocking(False)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    poller.register(s)

    while True:
        conns = poller.poll()
        for conn in conns:
            if s == conn:
                new_conn, remote_addr = conn.accept()
                print(f"remote_addr: {remote_addr}")
                new_conn.setblocking(False)
                new_conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                poller.register(new_conn)
            else:
                data = conn.recv(1024)

                if not data:
                    poller.unregister(conn)
                    conn.close()
                    print("socket: disconnected")
                    continue

                print(f"{conn.getpeername()} -> {data}")
                conn.send(data)
