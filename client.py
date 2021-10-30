import socket
import sys
import time
import keyboard

HOST, PORT = "192.168.8.101", 9999
data = "test message"

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    print("Connecting to " + str(HOST) + ":" + str(PORT) + "...")
    sock.connect((HOST, PORT))
    print("Connected...")

    while True:
        sock.send(bytes(data + " @ " + str(time.time())[8:], "utf-8"))
        if (keyboard.is_pressed('p')):
            break
        time.sleep(0.05)