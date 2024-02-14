from abc import ABC, abstractmethod
from state.base import (
    BaseState,
    Response,
    ReponseStatus,
    ProtocolContextChatObserver,
    Context,
    SenderCallback,
)
from state.sync_key_exchange import SyncKeyExchangeState
from state.key_exchange import KeyExchangeState
import json
from crypto import aes
from typing import Protocol
from network import Addr


class SessionCloseObserver(Protocol):
    def on_session_close(self, addr: Addr):
        pass


class Receiver(ABC):
    @abstractmethod
    def on_message_recv(self, raw_message: bytes) -> Response:
        pass


class Sender(ABC):
    @abstractmethod
    def send_message(self, message: bytes, sender_cb: SenderCallback):
        pass


class Close(ABC):
    @abstractmethod
    def close_session(self, addr: Addr, close_observer: SessionCloseObserver):
        pass


class ReceiverSender(Receiver, Sender, Close):
    pass


class BaseSession(ReceiverSender):
    def __init__(
        self, state: BaseState, addr: Addr, chat_observer: ProtocolContextChatObserver
    ) -> None:
        self._addr: Addr = addr
        self._chat_observer: ProtocolContextChatObserver = chat_observer
        self._state: BaseState = state

    def change_state(self, state: BaseState):
        self._state = state

    def on_message_recv(self, raw_message: bytes) -> Response:
        try:
            return self._state.on_message(
                raw_message,
                Context(
                    state_changer=self,
                    chat_observer=self._chat_observer,
                    addr=self._addr,
                ),
            )
        except Exception as e:
            print(f"exception caught: {e}")
            error_msg = {}
            error_msg["result"] = "invalid"
            return Response(
                message=json.dumps(error_msg).encode(),
                status=ReponseStatus.DISCONNECT,
            )

    def close_session(self, addr: Addr, close_observer: SessionCloseObserver):
        close_observer.on_session_close(self._addr)


class ServerSession(BaseSession):
    def __init__(self, addr: Addr, chat_observer: ProtocolContextChatObserver) -> None:
        BaseSession.__init__(self, SyncKeyExchangeState(), addr, chat_observer)

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        self._state.send_message(message, sender_cb)


class ClientSession(BaseSession):
    def __init__(self, addr: Addr, chat_observer: ProtocolContextChatObserver) -> None:
        BaseSession.__init__(
            self, KeyExchangeState(aes.generate_key()), addr, chat_observer
        )

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        self._state.send_message(message, sender_cb)


if __name__ == "__main__":

    class MockChatCallback:
        def on_chat(self, addr: Addr, message: bytes):
            print(message)

    class MockSender:
        def __init__(self) -> None:
            self.sent_msg: bytes = b""

        def send(self, cipher_message: bytes) -> int:
            self.sent_msg = cipher_message
            return len(cipher_message)

    mock_chat_observer = MockChatCallback()
    mock_client_sender = MockSender()
    mock_server_sender = MockSender()

    server_session = ServerSession(
        addr=Addr(host="localhost", port=1234), chat_observer=mock_chat_observer
    )
    client_session = ClientSession(
        addr=Addr(host="localhost", port=5678), chat_observer=mock_chat_observer
    )

    message = "hello"

    server_response = server_session.on_message_recv(b"")
    # print(server_response)
    client_response = client_session.on_message_recv(server_response.message)
    # print(client_response)

    server_response = server_session.on_message_recv(client_response.message)
    # print(server_response)

    client_session.send_message(
        b"helwrq3rlo", lambda data: mock_client_sender.send(data)
    )
    server_response = server_session.on_message_recv(mock_client_sender.sent_msg)

    server_session.send_message(
        b"123wofsdfld", lambda data: mock_server_sender.send(data)
    )
    client_session.on_message_recv(mock_server_sender.sent_msg)
