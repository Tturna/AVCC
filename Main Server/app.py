# This is the main server, which is supposed to combine all the demo servers into
# one convenient package, with the help of Wekinator and Oscullator.
# The server will receive accelerometer and gyroscope data from multiple Nano 33 IoT devices.

# Wanted Features:
# - Sending and receiving OSC messages to and from Wekinator
# - Sending OSC data to Oscullator, which communicates with Ableton

# This is a server to receive accelerometer and gyroscope data from the Nano 33 IoT.
# (not really) This is designed to calculate the board's relative position in the world.
# This is designed to receive data from the tracker.ino or trackerwireless.ino Arduino client

import selectors
import socket
import types
import tkgui
import server as avcc_server

sel = selectors.DefaultSelector()
server = avcc_server.Server("192.168.1.103")


# GUI event callbacks ----------------------------------
def button_listen(_):
    server.set_listening(True)
    host, port = server.get_host_and_port()

    # Create socket
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))

    # Start listening for connections
    lsock.listen()
    lsock.setblocking(False)

    # Set socket as monitored for incoming traffic
    sel.register(lsock, selectors.EVENT_READ, data=None)

    print('listening on', (host, port))
    tkgui.log_insert(-1, "Listening on " + host + ":" + str(port))


def button_stop(_):
    server.set_listening(False)

    # clear data
    server.clear_data()
    tkgui.clear_graphics()

    tkgui.log_delete("1.0", -1)
    tkgui.log_insert("1.0", "Stopped listening.")


# ------------------------------------------------------
def accept_wrapper(sock):
    # Accept connection and get a new socket that we listen to
    conn, addr = sock.accept()
    conn.setblocking(False)
    print('accepted connection from', addr)

    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


# Tkinter GUI
tkgui.setup(server.get_listen_timeout(), server.set_listen_timeout, button_listen, button_stop, server.set_visualize)

while True:
    tkgui.update()  # Update Tkinter GUI
    if not server.get_listening(): continue

    # Start monitoring registered objects (should just be our socket)
    # Timeout here so the program doesn't get suck on "listening..."
    # TODO: threading here?
    events = sel.select(timeout=server.get_listen_timeout())

    # If no events were found (e.g. timeout), stop listening
    if len(events) == 0:
        startedListening = False
        tkgui.log_delete("1.0", -1)
        tkgui.log_insert("1.0", "Timed out")

    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            server.service_connection(key, mask, sel)
