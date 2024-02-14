import tkinter as tk
from tkinter import scrolledtext
from typing import Protocol
from state.base import Addr


class ChatSentObserver(Protocol):
    def on_chat_message_sent(self, addr: Addr, message: str):
        pass


class ChatCloseObserver(Protocol):
    def on_chat_closes(self, addr: Addr):
        pass


class ChatScreen:
    def __init__(
        self,
        master: tk.Toplevel,
        target_addr: Addr,
        chat_sent_observer: ChatSentObserver,
        chat_close_observer: ChatCloseObserver,
    ):
        master.protocol("WM_DELETE_WINDOW", self.on_frame_close)
        self.master = master
        self.target_addr: Addr = target_addr
        self.chat_sent_observer: ChatSentObserver = chat_sent_observer
        self.chat_close_observer: ChatCloseObserver = chat_close_observer
        self.master.title(str(target_addr))

        self.chat_msg = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, width=60, height=20
        )
        self.chat_msg.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )  # Sticky option makes it expand in all directions

        self.message_label = tk.Label(master, text="Message:")
        self.message_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        # Log Message Entry
        self.message_entry = tk.Entry(master, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        # Log Button
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        # Configure row and column weights for resizing
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_columnconfigure(0, weight=1)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self._insert_message(message=f"you: {message}")
            self.chat_sent_observer.on_chat_message_sent(self.target_addr, message)

    def recv_message(self, message: str):
        self._insert_message(f"others: {message}")

    def close(self):
        self.on_frame_close()

    def _insert_message(self, message: str):
        self.chat_msg.insert(tk.END, f"{message}\n")
        self.message_entry.delete(0, tk.END)

    def on_frame_close(self):
        self.chat_close_observer.on_chat_closes(addr=self.target_addr)
        self.master.destroy()
