from state.base import BaseState, Response, ReponseStatus, Context, SenderCallback
import json
from crypto import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from typing import Optional
import base64
from state.ack_key_exchange import AckKeyExchangeState


class SyncKeyExchangeState(BaseState):
    def __init__(self) -> None:
        self.pri_key: Optional[RSAPrivateKey] = None

    @property
    def private_key(self) -> RSAPrivateKey:
        assert self.pri_key
        return self.pri_key

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        raise RuntimeError("sync key state, unable to send")

    def on_message(self, message: bytes, context: Context) -> Response:
        changer = context.state_changer

        pri_key, pub_key = rsa.generate_key_pair()
        pub_key_bytes = rsa.public_key_to_bytes(pub_key)
        self.pri_key = pri_key

        output_msg = {}
        output_msg["pub"] = base64.b64encode(pub_key_bytes).decode()

        response = Response(
            message=json.dumps(output_msg).encode(), status=ReponseStatus.REPLY_NEEDED
        )

        changer.change_state(AckKeyExchangeState(pri_key=pri_key))

        return response
