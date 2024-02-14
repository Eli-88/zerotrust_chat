from state.base import BaseState, Response, ReponseStatus, Context, SenderCallback

from state.chat import ChatState

import json
from crypto import rsa
from typing import Optional
import base64


class KeyExchangeState(BaseState):
    def __init__(self, secret: bytes) -> None:
        self._secret = secret

    @property
    def secret(self) -> Optional[bytes]:
        return self._secret

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        raise RuntimeError("key exchange state: unable to send message")

    def on_message(self, message: bytes, context: Context) -> Response:
        state_changer = context.state_changer

        input_msg = json.loads(message.decode())
        pub_key_bytes = base64.b64decode(input_msg["pub"].encode())
        pub_key = rsa.bytes_to_public_key(pub_key_bytes)

        cipher_secret = rsa.encrypt_message(pub_key, self._secret)

        output_msg = {}
        output_msg["secret"] = base64.b64encode(cipher_secret).decode()
        response = Response(
            message=json.dumps(output_msg).encode(),
            status=ReponseStatus.REPLY_NEEDED,
        )

        state_changer.change_state(ChatState(self._secret))

        return response
