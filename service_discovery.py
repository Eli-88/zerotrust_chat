import socket
import network
from state.base import Addr
from typing import Optional, Set, Iterable


class ServiceDiscoveryClient:
    def __init__(self, local_addr: Addr, multicast_addr: Addr) -> None:
        self.message: bytes = f"{local_addr.host}:{local_addr.port}".encode()
        self.multicast_addr = multicast_addr

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def publish(self) -> None:
        self.sock.sendto(
            self.message, (self.multicast_addr.host, self.multicast_addr.port)
        )


class ServiceDiscoveryServer:
    def __init__(self, local_addr: Addr, multicast_addr: Addr) -> None:
        self.local_addr = local_addr
        self.poller = network.Poller()
        self.active_address: Set[Addr] = set()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind(("", multicast_addr.port))
        self.mreq = socket.inet_aton(multicast_addr.host) + socket.inet_aton(
            local_addr.host
        )

        self.poller.register(self.sock)

    def poll(self, timeout: Optional[float] = None):
        for conn in self.poller.poll(timeout):
            assert conn == self.sock
            data, _ = conn.recvfrom(1024)

            try:
                host, port = data.decode().split(":")
                addr = Addr(host=host, port=int(port))
                if addr != self.local_addr:
                    self.active_address.add(addr)
            except Exception:
                pass

    def retrieve_active_address(self) -> Iterable[Addr]:
        return (addr for addr in self.active_address)


if __name__ == "__main__":
    import time

    discovery_client = ServiceDiscoveryClient(
        local_addr=Addr(host="127.0.0.1", port=5009),
        multicast_addr=Addr(host="224.0.0.1", port=5005),
    )

    discovery_client2 = ServiceDiscoveryClient(
        local_addr=Addr(host="127.0.0.1", port=7001),
        multicast_addr=Addr(host="224.0.0.1", port=5005),
    )

    discovery_server = ServiceDiscoveryServer(
        local_addr=Addr(host="127.0.0.1", port=5006),
        multicast_addr=Addr(host="224.0.0.1", port=5005),
    )

    start = time.time()

    while True:
        if time.time() - start > 3:
            discovery_client.publish()
            discovery_client2.publish()
            for addr in discovery_server.retrieve_active_address():
                print(addr)
            start = time.time()

        discovery_server.poll(0.05)
