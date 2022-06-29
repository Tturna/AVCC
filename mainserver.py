# This is the main server, which is supposed to combine all the demo servers into
# one convenient package. The server will receive accelerometer and gyroscope data
# from multiple Nano 33 IoT devices.

# Features:
#
# - Visualize orienation of 1 board in real time
# - Sending MIDI messages based on Arduino data
#   - different function options?
#       - Only use pitch for messages
#       - Use multiple Arduino inputs for messages
#   - Send different types of messages
# - Sending and receiving OSC messages to and from Wekinator (or other software) (?)

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

# List of monitor switch buttons
# this is used to turn all of them off except for the selected one,
# because only one board input can be monitored at once
monitorSwitches = []

# the socket that will be used for board orientation visualization
visualizedSock = None
visualize = False

firstsocket = None # Used to store the first connected socket. This will be used for visualizing

# Forward declare updating widgets
textlog = None
inputWidgets = {} # dict to store the pitch, roll and yaw values for each connected board

# Raylib shit
# init_window(800, 800, "Nano 33 Orientation Visualizer")
# mesh = gen_mesh_cube(35, 1, 10)
# model = load_model_from_mesh(mesh)

# cam = Camera3D(Vector3(0,10,10), Vector3(0,0,0), Vector3(0,1,0), 75, CameraProjection.CAMERA_PERSPECTIVE)
# set_camera_mode(cam, CameraMode.CAMERA_FREE)
# set_target_fps(30)

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
    listenTimeout = int(event.widget.get())
    print("Listen timeout changed to " + str(listenTimeout))

def UpdateInputWidget(sock, pry):
    global inputWidgets

    for n in range(3):
        label = inputWidgets[sock][n]
        label.delete("1.0", tk.END)
        label.insert("1.0", str(pry["pry"[n]]))

def SelectMonitorInput(checkButton, sock):
    global monitorSwitches
    global visualizedSock
    
    for ms in monitorSwitches:
        ms.deselect()

    checkButton.select()
    visualizedSock = sock

def SwitchVisualMonitor(state: bool):
    global visualize
    visualize = state
    print(state)

# Tkinter GUI
window = tk.Tk()
window.title("AVCC")
frame = tk.Frame(master=window, width=960, height=270)
frame.pack()
listenTitle = tk.Label(master=frame, text="Arduino Listener\n")
listenTitle.place(x=5,y=0)
# ipEntry = tk.Entry(width=15)
# ipEntry.insert(0, host)
# ipEntry.bind("<Return>", IPEntryChanged)
# ipEntry.pack()
timeoutLabel = tk.Label(master=frame, text="Listen Timeout")
timeoutLabel.place(x=5, y=30)
timeoutEntry = tk.Entry(master=frame, width=10)
timeoutEntry.insert(0, str(listenTimeout))
timeoutEntry.bind("<Return>", TimeoutEntryChanged) # Change to separate button?
timeoutEntry.place(x=5, y=50)
buttonCon = tk.Button(master=frame, text="Start Listening", width=12, height=2)
buttonCon.bind("<Button-1>", ButtonListen) # When mouse1 is pressed on this widget, run callback
buttonCon.place(x=5, y=70)
buttonStop = tk.Button(master=frame, text="Stop Listening", width=12, height=2)
buttonStop.bind("<Button-1>", ButtonStop)
buttonStop.place(x=105, y=70)
textlog = tk.Text(master=frame, width=50, height=1)
textlog.place(x=0, y=250)

connectionsLabel = tk.Label(master=frame, text="Connected devices:")
connectionsLabel.place(x=550, y=0)

visualizeLabel = tk.Label(master=frame, text="Visualize")
visualizeLabel.place(x=500, y=20)

for n in range(3):
    pryLabel = tk.Label(master=frame, text=["Pitch", "Roll", "Heading"][n])
    pryLabel.place(x=700 + 75*n, y=20)

visualizeTitle = tk.Label(master=frame, text="Visual Orientation Monitor")
visualizeTitle.place(x=5, y=130)

startVisButton = tk.Button(master=frame, text="Start Monitor", width=12, height=2, command=lambda: SwitchVisualMonitor(True))
stopVisButton = tk.Button(master=frame, text="Stop Monitor", width=12, height=2, command=lambda: SwitchVisualMonitor(False))

startVisButton.place(x=5, y=150)
stopVisButton.place(x=105, y=150)

def accept_wrapper(sock):

    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    global textlog
    global boardinputs
    global inputWidgets
    global messages
    global firstsocket
    global monitorSwitches

    sock = key.fileobj
    data = key.data

    if (sock not in boardinputs.keys()):
        boardinputs[sock] = {"p": 0.0, "r": 0.0, "y": 0.0}
        inputWidgets[sock] = []
        messages[sock] = ""
        print(f"Added {sock} to boardinputs.")
        if (firstsocket == None): firstsocket = sock

        connCount = len(boardinputs.keys())
        connLabel = tk.Label(master=frame, text=f"{str(connCount)}: {str(sock.getpeername())}")
        connLabel.place(x=550, y=40*connCount)

        monitorCheckButton = tk.Checkbutton(master=frame, command=lambda: SelectMonitorInput(monitorCheckButton, sock))
        monitorCheckButton.place(x=500, y=40*connCount)
        monitorSwitches.append(monitorCheckButton)

        for n in range(3):
            pryText = tk.Text(master=frame, width=8, height=1)
            pryText.insert("1.0", str(boardinputs[sock]["pry"[n]]))
            inputWidgets[sock].append(pryText)
            pryText.place(x=700 + 75*n, y=40*connCount)

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
                        num = float(value)
                        pry[l] = num
                        value = ""
                        newmsg = message[n:]
                else:
                    value += l

            # Update value on GUI
            UpdateInputWidget(sock, pry)

            #print(pry)
            #print(sock.getpeername())
            #_, peerport = sock.getpeername()
            #print(f"{peerport}: {pry}\n")

            if (visualize and sock == visualizedSock):

                # # Calculate the transform matrix
                # # Following this:
                # # https://docs.arduino.cc/library-examples/curie-imu/Genuino101CurieIMUOrientationVisualiser
                # radr = math.radians(pry["r"])
                # radp = math.radians(pry["p"])
                # rady = math.radians(pry["y"])
                # c1 = math.cos(-radr)
                # s1 = math.sin(-radr)
                # c2 = math.cos(radp)
                # s2 = math.sin(radp)
                # c3 = math.cos(-rady)
                # s3 = math.sin(-rady)
                # bigboimatrix = Matrix(  c2*c3,  s1*s3+c1*c3*s2, c3*s1*s2-c1*s3, 0,
                #                         -s2,    c1*c2, c2*s1,   0,
                #                         c2*s3,  c1*s2*s3-c3*s1, c1*c3+s1*s2*s3, 0,
                #                         0,      0,              0,              1)

                # update_camera(cam)
                # begin_drawing()
                # clear_background(Color(0,0,0,255))
                # begin_mode_3d(cam)

                # model.transform = bigboimatrix
                # draw_model(model, Vector3(0,0,0), 1, Color(255,0,0,255))
                # draw_grid(50,1)

                # end_mode_3d()
                # end_drawing()
                pass

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
    window.update() # Update Tkinter GUI
    if startedListening == False: continue

    # Timeout here so the program doesn't get suck on "listening..."
    # threading here?
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
