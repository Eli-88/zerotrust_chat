import tkinter as tk
import service_discovery
from network import Addr
import chat_manager
from screen.connect_screen import ConnectionScreen
from screen.chat_screen import ChatScreen
from typing import Dict
import sys


class App:
    def __init__(self, local_addr: Addr, multicast_addr: Addr) -> None:
        self.root = tk.Tk()
        self.connect_screen = ConnectionScreen(self.root, self)
        self.all_chatscreens: Dict[Addr, ChatScreen] = {}

        self.service_discovery_client = service_discovery.ServiceDiscoveryClient(
            local_addr=local_addr, multicast_addr=multicast_addr
        )

        self.service_discovery_server = service_discovery.ServiceDiscoveryServer(
            local_addr=local_addr, multicast_addr=multicast_addr
        )

        self.chat_manager = chat_manager.ChatManager(
            host_addr=local_addr, chat_recv_observer=self, session_close_observer=self
        )

        self.run_service_discovery_task()
        self.run_chat_manager_task()

    def loop(self):
        self.root.mainloop()

    def on_connect(self, addr: Addr):
        # triggered by connect screen
        if addr not in self.all_chatscreens.keys():
            self.chat_manager.start_new_connection(addr)
            self.all_chatscreens[addr] = ChatScreen(
                tk.Toplevel(self.root),
                addr,
                chat_sent_observer=self,
                chat_close_observer=self,
            )

    def on_chat_message_sent(self, addr: Addr, message: str):
        self.chat_manager.send_message(addr, message=message.encode())

    def on_chat(self, addr: Addr, message: bytes):
        if addr not in self.all_chatscreens.keys():
            self.all_chatscreens[addr] = ChatScreen(
                tk.Toplevel(self.root),
                addr,
                chat_sent_observer=self,
                chat_close_observer=self,
            )

        self.all_chatscreens[addr].recv_message(message=message.decode())

    def on_chat_closes(self, addr: Addr):
        if addr in self.all_chatscreens.keys():
            self.all_chatscreens.pop(addr)

        self.chat_manager.close_conn(addr)

    def on_session_close(self, addr: Addr):
        print(f"on session close {addr}")
        if addr in self.all_chatscreens.keys():
            self.all_chatscreens[addr].close()
            self.all_chatscreens.pop(addr)

    def run_service_discovery_task(self):
        def poll():
            self.service_discovery_server.poll(timeout=0.01)
            self.connect_screen.update_active_ip(
                self.service_discovery_server.retrieve_active_address()
            )
            self.root.after(500, poll)

        poll()

        def publish_for_service_discovery():
            self.service_discovery_client.publish()
            self.root.after(3000, publish_for_service_discovery)

        publish_for_service_discovery()

    def run_chat_manager_task(self):
        def poll():
            self.chat_manager.run(0.1)
            self.root.after(100, poll)

        poll()


def main():
    if len(sys.argv) < 2:
        print("usage: python app.py <port>")

    local_addr = Addr(host="127.0.0.1", port=int(sys.argv[1]))
    multicast_addr = Addr(host="224.0.0.1", port=5005)

    app = App(local_addr=local_addr, multicast_addr=multicast_addr)
    app.loop()


if __name__ == "__main__":
    main()
