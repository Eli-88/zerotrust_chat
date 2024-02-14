from state.base import BaseState, Response, ReponseStatus, Context, SenderCallback
import json
from crypto import aes


class ChatState(BaseState):
    def __init__(self, secret: bytes) -> None:
        self.secret: bytes = secret

    def on_message(self, message: bytes, context: Context) -> Response:
        chat_observer = context.chat_observer
        addr = context.addr

        input_msg = json.loads(message.decode())
        recv_msg = aes.decrypt_message(self.secret, input_msg["message"].encode())

        chat_observer.on_chat(addr=addr, message=recv_msg)
        return Response(
            message=b"",
            status=ReponseStatus.REPLY_NOT_NEEDED,
        )

    def send_message(self, message: bytes, sender_cb: SenderCallback):
        cipher_message = aes.encrypt_message(self.secret, message)
        output_msg = {}
        output_msg["message"] = cipher_message.decode()
        sender_cb(json.dumps(output_msg).encode())
