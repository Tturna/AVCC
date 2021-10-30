import selectors
import socket
import types
from pythonosc.udp_client import SimpleUDPClient
import keyboard

sel = selectors.DefaultSelector()
# ...
host = "192.168.8.101"
port = 9999
message = ""
xyz = [0, 0, 0]

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# Set up an OSC Client
oscClient = SimpleUDPClient("127.0.0.1", 9998)

def SendOSCMessage(xyz):
    try:
        if (float(xyz[0]) + float(xyz[1]) + float(xyz[2]) >= 300):
            print("------------------------------Sending OSC...")
            oscClient.send_message("localhost", 35)
    except:
        print("Failed to send OSC")

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    global message
    global xyz

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(512)  # Should be ready to read
        except Exception as e:
            print(e)
            recv_data = None

        if recv_data:
            data.outb += recv_data
            message += str(repr(data.outb))[1:]

            # Message processor
            dotCount = 0
            for i in range(len(message) - 1):
                if (message[i] == "."):
                    dotCount += 1
            
            # Remove excess characters
            safe = 0
            while (message.find("'") != -1):

                if (safe >= 10):
                    print("shit broke")
                    break

                ind = message.find("'")
                if (ind == 0):
                    message = message[1:]
                elif (ind == len(message) - 1):
                    message = message[:-1]
                else:
                    message = message[:ind] + message[ind + 1:]
                
                safe += 1

            if (dotCount >= 3): # If message has values for all x, y and z
                # Parse the x, y and z values from the message
                xyzStrings = ["x", "y", "z"]

                skip = True
                for i in range(len(xyz)):
                    dotIndex = message.find(".")

                    # Make sure the message has all the values
                    # If not, read another message
                    if (skip):
                        tmpMsg = message
                        for n in range(2):
                            di = tmpMsg.find(".")
                            tmpMsg = tmpMsg[di + 3:]
                        
                        if (dotIndex > len(tmpMsg) - 3):
                            break
                        else:
                            skip = False

                    xyz[i] = message[:dotIndex + 3]
                    message = message[dotIndex + 3:]
                    print(xyzStrings[i] + ": " + str(xyz[i]))
                SendOSCMessage(xyz)
                print("")

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