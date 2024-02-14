import network
from typing import Optional, Tuple, Dict, NamedTuple
import socket
import session
from state.base import ReponseStatus
from network import Addr


class ConnSessionPair(NamedTuple):
    conn: socket.socket
    session: session.ReceiverSender


class ChatManager:
    def __init__(
        self,
        host_addr: Addr,
        chat_recv_observer: session.ProtocolContextChatObserver,
        session_close_observer: session.SessionCloseObserver,
    ) -> None:
        self.chat_recv_observer: session.ProtocolContextChatObserver = (
            chat_recv_observer
        )
        self.session_close_observer: session.SessionCloseObserver = (
            session_close_observer
        )
        self.addr_conn_mapping: Dict[Addr, ConnSessionPair] = {}
        self.poller = network.Poller()
        self.server_socket = self._create_tcp_server(host_addr)

    def close_conn(self, addr: Addr):
        conn_session = self.addr_conn_mapping.get(addr, None)
        if conn_session:
            conn, session = conn_session
            session.close_session(addr, self.session_close_observer)
            self._close_conn(conn)
            del self.addr_conn_mapping[addr]

    def run(self, timeout: Optional[float] = None):
        conns = self.poller.poll(timeout=timeout)
        for conn in conns:
            if conn == self.server_socket:
                conn_session, addr = self._accept_new_conn(conn)
                self.addr_conn_mapping[addr] = conn_session
            else:
                try:
                    recv_data = conn.recv(1024)

                    if not recv_data:
                        self._close_conn(conn)
                        continue

                    remote_host, remote_port = conn.getpeername()
                    conn_session = self.addr_conn_mapping.get(
                        Addr(host=remote_host, port=remote_port), None
                    )
                    assert conn_session is not None
                    response = conn_session.session.on_message_recv(recv_data)

                    if response.status == ReponseStatus.DISCONNECT:
                        self._close_conn(conn)
                        continue

                    if response.status == ReponseStatus.REPLY_NEEDED:
                        conn.send(response.message)

                except Exception as e:
                    print(f"conn exception: {e}")
                    self._close_conn(conn)

    def on_chat(self, addr: Addr, message: bytes):
        self.chat_recv_observer.on_chat(addr, message)

    def send_message(self, dest_addr: Addr, message: bytes):
        conn_session = self.addr_conn_mapping.get(dest_addr, None)
        if conn_session:
            conn_session.session.send_message(
                message, lambda data: conn_session.conn.send(data)
            )

    def start_new_connection(self, dest_addr: Addr) -> None:
        assert self.addr_conn_mapping.get(dest_addr, None) is None

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        conn.connect((dest_addr.host, dest_addr.port))

        self.poller.register(conn)

        remote_host, remote_port = conn.getpeername()

        if not self.addr_conn_mapping.get(dest_addr, None):
            self.addr_conn_mapping[
                Addr(host=remote_host, port=remote_port)
            ] = ConnSessionPair(
                conn=conn,
                session=session.ClientSession(addr=dest_addr, chat_observer=self),
            )

        conn.send(b"hello")  # send something to start key exchange handshake

    def _create_tcp_server(self, addr: Tuple[str, int]) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        sock.bind(addr)
        sock.listen()

        self.poller.register(sock)
        return sock

    def _accept_new_conn(self, conn: socket.socket) -> Tuple[ConnSessionPair, Addr]:
        new_conn, remote_addr = conn.accept()
        new_conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.poller.register(new_conn)
        host, port = remote_addr

        return (
            ConnSessionPair(
                conn=new_conn,
                session=session.ServerSession(
                    Addr(host=host, port=port), chat_observer=self
                ),
            ),
            Addr(host=host, port=port),
        )

    def _close_conn(self, conn: socket.socket):
        try:
            print(f"connection close: {conn}")
            self.poller.unregister(conn)
            conn.close()
        except Exception:
            pass
