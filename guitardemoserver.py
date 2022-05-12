import selectors
import socket
import types
import time
import os
import keyboard
import tkinter as tk
from pythonosc.udp_client import SimpleUDPClient
from simplecoremidi import send_midi

sel = selectors.DefaultSelector()
# ...
host = socket.gethostbyname(socket.gethostname())
port = 9999
message = ""
startedListening = False
listenTimeout = 15

# midi stuff
midiChannel = 1
note_on_action = 0x90
velocity = 127

# Set up an OSC Client to send data to Wekinator
# oscClient = SimpleUDPClient("127.0.0.1", 9998)
lastY = 0

# Forward declare text log widget
textlog = None

# GUI event callbacks
def ButtonListen(event):
    global startedListening
    global host
    global textlog

    # socket stuff. TBF can't remember how this works. 
    startedListening = True
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    print('listening on', (host, port))
    textlog.insert(tk.END, "Listening on " + host + ":" + str(port))

def ButtonStop(event):
    global startedListening
    global textlog

    startedListening = False
    textlog.delete("1.0", tk.END)
    textlog.insert("1.0", "Stopped listening.")

def TimeoutEntryChanged(event):
    global listenTimeout
    listenTimeout = event.widget.get()
    print("Listen timeout changed to " + str(listenTimeout))

# GUI
window = tk.Tk()
window.title("AVCC")
title = tk.Label(text="Arduino Listener\n")
title.pack()
# ipEntry = tk.Entry(width=15)
# ipEntry.insert(0, host)
# ipEntry.bind("<Return>", IPEntryChanged)
# ipEntry.pack()
timeoutLabel = tk.Label(text="Listen Timeout")
timeoutLabel.pack()
timeoutEntry = tk.Entry(width=15)
timeoutEntry.insert(0, str(listenTimeout))
timeoutEntry.bind("<Return>", TimeoutEntryChanged)
timeoutEntry.pack()
buttonCon = tk.Button(text="Start Listening", width=12, height=2)
buttonCon.bind("<Button-1>", ButtonListen) # When mouse1 is pressed on this widget, run callback
buttonCon.pack()
buttonStop = tk.Button(text="Stop Listening", width=12, height=2)
buttonStop.bind("<Button-1>", ButtonStop)
buttonStop.pack()
textlog = tk.Text(width=50, height=1)
textlog.pack()

# OSC stuff
def SendOSCMessage(gyroXYZ, accXYZ):
    """
    global lastY

    try:
        # Check if the board was whacked like a drum stick
        thresh = 300.0

        print("test")
        if (abs(float(gyroXYZ[1])) >= thresh and abs(lastY) < thresh):
            print("------------------------------Sending OSC...")
            oscClient.send_message("/wek/inputs", 1)
        
        lastY = float(gyroXYZ[1])
    except Exception as e:
        print("Failed to send OSC.")
        print(e)
    """

    # Send accelerometer data to wekinator
    #oscClient.send_message("/wek/inputs", (gyroXYZ[0], gyroXYZ[1], gyroXYZ[2]))

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    global message
    global textlog

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(512)  # Should be ready to read
        except Exception as e:
            print(e)
            recv_data = None

        if recv_data: # Message has been read
            data.outb += recv_data
            message += str(repr(data.outb))[1:]
            message.replace("'", "")

            print(message)
            #SendOSCMessage(gyroXYZ, accXYZ)

            #send_midi((0xB0 | 1, 40, gyroXYZ[2]))

                #print(str(repr(data.outb))[1:], 'from', data.addr)
                #print(message)
            data.outb = bytes(0)
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE & False:
        if data.outb:
            try:
                sent = sock.send(data.outb)  # Should be ready to write
            except Exception as e:
                print(e)
            data.outb = data.outb[sent:]

#window.mainloop()

while True:
    window.update() # Update GUI
    if startedListening == False: continue

    # Timeout here so the program doesn't get suck on "listening..."
    events = sel.select(timeout=10)

    # If no events were found (e.g. timeout), stop listening
    if len(events) == 0:
        startedListening = False
        textlog.delete("1.0", tk.END)
        textlog.insert("1.0", "Timed out")
    
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)