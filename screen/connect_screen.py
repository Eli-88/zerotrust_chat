import tkinter as tk
from tkinter import ttk
from typing import Iterable, Protocol
from state.base import Addr


class ConnectObserver(Protocol):
    def on_connect(self, addr: Addr):
        pass


class ConnectionScreen:
    def __init__(self, master: tk.Tk, connect_observer: ConnectObserver):
        self.master = master
        self.connect_observer: ConnectObserver = connect_observer
        self.master.title("Connection")

        # Label
        self.connect_label = tk.Label(master, text="Connect:")
        self.connect_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)

        # Combobox
        self.combo_var = tk.StringVar()
        self.combo_box = ttk.Combobox(master, textvariable=self.combo_var, values=[])
        self.combo_box.set("Select an ip")
        self.combo_box.grid(row=0, column=1, padx=10, pady=5)

        # Button
        self.connect_button = tk.Button(master, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=2, padx=10, pady=5)

    def connect(self):
        addr = self.combo_var.get()
        host, port = addr.split(":")
        self.connect_observer.on_connect(Addr(host=host, port=int(port)))

    def update_active_ip(self, active_ip: Iterable[Addr]):
        self.combo_box["values"] = list(
            f"{addr.host}:{addr.port}" for addr in active_ip
        )
