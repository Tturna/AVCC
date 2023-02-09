import socket
import tkgui
from pythonosc.udp_client import SimpleUDPClient
from selectors import SelectorKey, DefaultSelector, EVENT_READ
from typing import Tuple


class Server:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 9999,
                 listen_timeout: int = 60) -> None:

        # Pitch, Roll, Yaw from the boards
        # this will be a nested dictionary
        self.__board_inputs = {}
        self.__messages = {}

        self.__host = host
        self.__port = port
        self.__listen_timeout = listen_timeout

        # the socket that will be used for board orientation visualization
        self.__visualized_sock = None
        self.__visualize = False
        self.__started_listening = False

        # initialize OSC Client
        self.__osc_client = SimpleUDPClient("192.168.1.101", 8000)

    def select_monitor_input(self, check_button, sock):
        tkgui.deselect_monitor_switches()
        check_button.select()
        self.__visualized_sock = sock

    def add_board_input(self, sock):
        self.__board_inputs[sock] = {"p": 0.0, "r": 0.0, "y": 0.0}
        self.__messages[sock] = ""
        tkgui.inputWidgets[sock] = []

        print(f"Added {sock} to boardinputs.")

        # if (firstsocket == None): firstsocket = sock

        conn_count = len(self.__board_inputs.keys())

        tkgui.place_label(
            f"{str(conn_count)}: {str(sock.getpeername())}",
            350,
            40 * conn_count
        )

        tkgui.add_monitor_switch(sock, self.select_monitor_input, 300, 40 * conn_count)
        tkgui.append_pry_texts(sock, self.__board_inputs[sock], 500, 40 * conn_count)
        tkgui.add_settings_button(725, 40 * conn_count)

    def clear_data(self):
        self.__board_inputs.clear()
        self.__messages.clear()

    def send_osc_message(self, values, address="/Arduino/Default"):
        self.__osc_client.send_message(address, values)

    def process_message(self, data, recv_data, sock):
        message = self.__messages[sock]
        pry = self.__board_inputs[sock]

        data.outb += recv_data
        message += str(repr(data.outb))[1:]
        message = message.replace("'", "")

        # get actual numbers from the received message
        # the system likes to send data in random ass amounts at a time so we gotta check when we have full messages

        value = ""
        newmsg = message
        for i, letter in enumerate(message):

            if letter not in "pry":
                value += letter
                continue

            if len(value) <= 2: continue

            num = float(value)
            pry[letter] = num
            value = ""
            newmsg = message[i:]

        # Update value on GUI
        tkgui.update_input_widget(sock, pry)

        self.send_osc_message(address=f'/arduino/{str(sock.getsockname()[0])}', values=pry.values())

        data.outb = bytes(0)
        self.__board_inputs[sock] = pry
        self.__messages[sock] = newmsg

    def service_connection(self, key: SelectorKey, mask: int, sel: DefaultSelector):
        sock = key.fileobj
        data = key.data

        if sock not in self.__board_inputs.keys():
            self.add_board_input(sock)

        if mask & EVENT_READ:
            try:
                recv_data = sock.recv(512)  # Should be ready to read
            except Exception as e:
                print(e)
                recv_data = None

            if recv_data:  # Message has been read
                self.process_message(data, recv_data, sock)
            else:
                print('closing connection to', data.addr)
                sel.unregister(sock)
                sock.close()

        # if mask & selectors.EVENT_WRITE & False:
        #     if data.outb:
        #         try:
        #             sent = sock.send(data.outb)  # Should be ready to write
        #         except Exception as e:
        #             print(e)
        #         data.outb = data.outb[sent:]

    def get_host_and_port(self) -> Tuple[str, int]:
        return self.__host, self.__port

    def set_listening(self, state: bool):
        self.__started_listening = state

    def get_listening(self) -> bool:
        return self.__started_listening

    def set_listen_timeout(self, seconds: int):
        self.__listen_timeout = seconds

    def get_listen_timeout(self) -> int:
        return self.__listen_timeout

    def set_visualized_sock(self, sock):
        self.__visualized_sock = sock

    def set_visualize(self, state: bool):
        self.__visualize = state
