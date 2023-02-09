# This is a server to receive accelerometer and gyroscope data from the Nano 33 IoT.
# This is designed to calculate the board's relative position in the world.
# This is designed to receive data from the tracker.ino Arduino client

import selectors
import socket
import types
import tkinter as tk
import math
from pyray import *

sel = selectors.DefaultSelector()
# ...
host = socket.gethostbyname(socket.gethostname())
port = 9999
messages = {}
startedListening = False
listenTimeout = 20

# Pitch, Roll, Yaw from the boards
# this will be a nested dictionary
boardinputs = {}

firstsocket = None # Used to store the first connected socket. This will be used for visualizing

# Forward declare text log widget
textlog = None

init_window(800, 800, "Nano 33 Orientation Visualizer")
mesh = gen_mesh_cube(35, 1, 10)
model = load_model_from_mesh(mesh)

cam = Camera3D(Vector3(0,10,10), Vector3(0,0,0), Vector3(0,1,0), 75, CameraProjection.CAMERA_PERSPECTIVE)
set_camera_mode(cam, CameraMode.CAMERA_FREE)
set_target_fps(30)

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
    global messages
    global textlog
    global firstsocket # temp

    sock = key.fileobj
    data = key.data

    if (sock not in boardinputs.keys()):
        boardinputs[sock] = {"p": 0.0, "r": 0.0, "y": 0.0}
        messages[sock] = ""
        print(f"Added {sock} to boardinputs.")
        if (firstsocket == None): firstsocket = sock

    pry = boardinputs[sock]
    message = messages[sock]

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

            #print(pry)
            #print(sock.getpeername())
            _, peerport = sock.getpeername()
            print(f"{peerport}: {pry}\n")

            if (firstsocket == sock):

                # Calculate the transform matrix
                # Following this:
                # https://docs.arduino.cc/library-examples/curie-imu/Genuino101CurieIMUOrientationVisualiser
                radr = math.radians(pry["r"])
                radp = math.radians(pry["p"])
                rady = math.radians(pry["y"])
                c1 = math.cos(-radr)
                s1 = math.sin(-radr)
                c2 = math.cos(radp)
                s2 = math.sin(radp)
                c3 = math.cos(-rady)
                s3 = math.sin(-rady)
                bigboimatrix = Matrix(  c2*c3, s1*s3+c1*c3*s2, c3*s1*s2-c1*s3, 0,
                                        -s2, c1*c2, c2*s1, 0,
                                        c2*s3, c1*s2*s3-c3*s1, c1*c3+s1*s2*s3, 0,
                                        0,0,0,1)

                update_camera(cam)
                begin_drawing()
                clear_background(Color(0,0,0,255))
                begin_mode_3d(cam)

                model.transform = bigboimatrix
                draw_model(model, Vector3(0,0,0), 1, Color(255,0,0,255))
                #draw_cube_wires(Vector3(0,0,0), 35, 1, 10, Color(127,0,0,255))
                #draw_cube(Vector3(0,0,0), 3, 3, 3, Color(0,127,255,255))
                draw_grid(50,1)

                end_mode_3d()
                end_drawing()

            data.outb = bytes(0)
            boardinputs[sock] = pry
            messages[sock] = newmsg
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
    events = sel.select(timeout=listenTimeout)

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
