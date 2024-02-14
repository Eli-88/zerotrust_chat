from abc import ABC, abstractmethod
from typing import NamedTuple, Any, Protocol, Callable
from enum import Enum
from network import Addr


class ContextKey:
    STATE_CHANGER = "state_changer"
    CHAT_OBSERVER = "chat_observer"
    ADDR = "addr"


class ProtocolContextStateChanger(Protocol):
    def change_state(self, state: Any):
        pass


class ProtocolContextChatObserver(Protocol):
    def on_chat(self, addr: Addr, message: bytes):
        pass


class Context(NamedTuple):
    state_changer: ProtocolContextStateChanger
    chat_observer: ProtocolContextChatObserver
    addr: Addr


class ReponseStatus(Enum):
    REPLY_NEEDED = 0
    REPLY_NOT_NEEDED = 1
    DISCONNECT = 2


class Response(NamedTuple):
    message: bytes
    status: ReponseStatus


SenderCallback = Callable[[bytes], int]


class BaseState(ABC):
    @abstractmethod
    def on_message(self, message: bytes, context: Context) -> Response:
        pass

    @abstractmethod
    def send_message(self, message: bytes, sender_cb: SenderCallback):
        pass
