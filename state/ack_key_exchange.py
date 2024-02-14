from state.base import BaseState, Response, ReponseStatus, Context, SenderCallback
import json
from crypto import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from typing import Optional
import base64
from state.chat import ChatState


class AckKeyExchangeState(BaseState):
    def __init__(self, pri_key: RSAPrivateKey) -> None:
        self.pri_key = pri_key
        self._secret: Optional[bytes] = None

    @property
    def secret(self) -> bytes:
        assert self._secret
        return self._secret

    def on_message(self, message: bytes, context: Context) -> Response:
        state_changer = context.state_changer

        input_msg = json.loads(message.decode())
        cipher_secret = base64.b64decode(input_msg["secret"].encode())

        self._secret = rsa.decrypt_message(self.pri_key, cipher_secret)

        response = Response(message=b"", status=ReponseStatus.REPLY_NOT_NEEDED)

        state_changer.change_state(ChatState(secret=self._secret))

        return response

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        raise RuntimeError("ack key state, unable to send message")
