import selectors
import socket
import types
import time
import os
from pythonosc.udp_client import SimpleUDPClient
import keyboard
from simplecoremidi import send_midi

sel = selectors.DefaultSelector()
# ...
host = "192.168.8.105"
port = 9999
message = ""
gyroXYZ = [0, 0, 0]
accXYZ = [0, 0, 0]

# midi stuff
midiChannel = 1
note_on_action = 0x90
velocity = 127

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# Set up an OSC Client to send data to Wekinator
oscClient = SimpleUDPClient("127.0.0.1", 9998)
lastY = 0

def SendOSCMessage(gyroXYZ, accXYZ):
    global lastY

    """
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
    oscClient.send_message("/wek/inputs", (gyroXYZ[0] + 0.0, gyroXYZ[1] + 0.0, gyroXYZ[2] + 0.0))

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    global message
    global gyroXYZ
    global accXYZ

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

            # |||||||||||||||||||||||||||||||||| --- OLD SHIT --- ||||||||||||||||||||||||||
            # # Message processor
            # dotCount = 0
            # for i in range(len(message) - 1):
            #     if (message[i] == "."):
            #         dotCount += 1
            
            # # Remove excess characters
            # safe = 0
            # while (message.find("'") != -1):

            #     if (safe >= 10):
            #         print("shit broke")
            #         break

            #     ind = message.find("'")
            #     if (ind == 0):
            #         message = message[1:]
            #     elif (ind == len(message) - 1):
            #         message = message[:-1]
            #     else:
            #         message = message[:ind] + message[ind + 1:]
                
            #     safe += 1

            # if (dotCount >= 4): # If message has values for all x, y and z
            #     # Parse the x, y and z values from the message
            #     gyroXYZStrings = ["x", "y", "z"]

            #     skip = True
            #     for i in range(len(gyroXYZ)):
            #         dotIndex = message.find(".")

            #         # Make sure the message has all the values
            #         # If not, read another message
            #         if (skip):
            #             tmpMsg = message
            #             for n in range(2):
            #                 di = tmpMsg.find(".")
            #                 tmpMsg = tmpMsg[di + 3:]
                        
            #             if (dotIndex > len(tmpMsg) - 3):
            #                 break
            #             else:
            #                 skip = False

            #         gyroXYZ[i] = float(message[:dotIndex + 3])
            #         message = message[dotIndex + 3:]
            #         print(gyroXYZStrings[i] + ": " + str(gyroXYZ[i]))

            # ||||||||||||||||||||||||||||||||||| --- NEW SHIT --- |||||||||||||||||||||||||||||||||

            message = message.replace("'", "")

            if ("g" in message and "a" in message):
                message = message[message.find("g"):]
                gyroXYZ[0] = float(message[message.find("g") + 1:message.find(",")])
                message = message[message.find(",") + 1:]
                gyroXYZ[1] = float(message[:message.find(",")])
                message = message[message.find(",") + 1:]
                gyroXYZ[2] = float(message[:message.find("a")])
            
            if ("a" in message and "e" in message):
                message = message[message.find("a"):]
                accXYZ[0] = float(message[message.find("a") + 1:message.find(",")])
                message = message[message.find(",") + 1:]
                accXYZ[1] = float(message[:message.find(",")])
                message = message[message.find(",") + 1:]
                accXYZ[2] = float(message[:message.find("e")])

            print("G: " + str(gyroXYZ) + " | A: " + str(accXYZ))
            #SendOSCMessage(gyroXYZ, accXYZ)

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

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
