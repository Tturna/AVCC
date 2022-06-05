# This is a server to receive accelerometer and gyroscope data from the Nano 33 IoT.
# This is designed to calculate the board's relative position in the world.
# This is designed to receive data from the tracker.ino Arduino client

import selectors
import socket
from turtle import pos
import types
import time
import tkinter as tk
import math
from numpy import size
from raylib import GenMeshCube
from vpython import vector, color, box, arrow

sel = selectors.DefaultSelector()
# ...
host = socket.gethostbyname(socket.gethostname())
port = 9999
message = ""
startedListening = False
listenTimeout = 15

# Pitch, Roll, Yaw from the board
pry = {
    "p": 0.0,
    "r": 0.0,
    "y": 0.0
}

oldpry = {
    "p": 0.0,
    "r": 0.0,
    "y": 0.0
}

# variable to store the time of the last message
# used to calculate deltatime between messages
# deltatime is used to smooth 3D animations
lastMessageTime = time.time()

# Open a browser window and draw a cuboid representing the Arduino board
boxsize = vector(3.5, .1, 1)
arrowlen = 2.5
arrowthicc = .02
redbox = box(pos=vector(0,0,0),axis=vector(1,0,0), size=boxsize)
xarw = arrow(length=arrowlen, shaftwidth=arrowthicc, axis=vector(1,0,0), color=color.red)
yarw = arrow(length=arrowlen, shaftwidth=arrowthicc, axis=vector(0,1,0), color=color.green)
zarw = arrow(length=arrowlen, shaftwidth=arrowthicc, axis=vector(0,0,1), color=color.blue)
farw = arrow(length=arrowlen, shaftwidth=arrowthicc, axis=vector(1,0,0), color=color.orange)
uarw = arrow(length=arrowlen, shaftwidth=arrowthicc, axis=vector(0,1,0), color=color.cyan)

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
    global lastMessageTime
    global redbox
    global arw

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
            message = message.replace("'", "")

            # get actual numbers from the received message
            # the system likes to send data in random ass amounts at a time so we gotta check when we have full messages

            value = ""
            newmsg = message
            for n in range(len(message)):
                l = message[n]
                if l in "pry":
                    if len(value) > 2:
                        pry[l] = float(value)
                        value = ""
                        newmsg = message[n:]
                else:
                    value += l

            print(pry)

            # calculate deltatime
            now = time.time()
            deltaTime = now - lastMessageTime
            lastMessageTime = now

            # calculate the angle degrees to rotate by
            # axes = [vector(1,0,0), vector(0,0,1), vector(0,1,0)]
            # for n in range(3):
            #     l = "pry"[n]
            #     degrees = pry[l] - oldpry[l]
            #     redbox.rotate(degrees* (math.pi / 180), axes[n])
            #     oldpry[l] = pry[l]

            # redbox.axis = vector(pry["p"], pry["y"], pry["r"]).norm()
            # redbox.size = boxsize

            x = -math.cos(pry["y"] * (math.pi / 180))
            z = math.sin(pry["y"] * (math.pi / 180))

            #x = math.cos(pry["r"] * (math.pi / 180))
            #y = -math.sin(pry["r"] * (math.pi / 180))

            uy = math.cos(pry["r"] * (math.pi / 180))
            ux = math.sin(pry["r"] * (math.pi / 180))

            axisvector = vector(x,0,z).norm()
            redbox.axis = axisvector
            farw.axis = axisvector

            upvector = vector(ux, uy, 0).norm()
            redbox.up = upvector
            uarw.axis = upvector
            
            redbox.size = boxsize

            data.outb = bytes(0)
            message = newmsg
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
