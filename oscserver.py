# This server was made to receive OSC messages from Wekinator and
# send MIDI messages according to received data.

from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from simplecoremidi import send_midi
from time import sleep

channel = 1
note_on_action = 0x90
velocity = 127

note = 60

# Set up an OSC Server to receive data from Wekinator
def print_handler(address, *args):
    print(f"{address}: {args}")

def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

    if ("Circle" in str(address)):
        print("Sending MIDI...")
        send_midi((note_on_action | channel, note, velocity))
        sleep(0.25)
        send_midi((note_on_action | channel, note, 0))

dispatcher = Dispatcher()
dispatcher.map("/something/*", print_handler)
dispatcher.set_default_handler(default_handler)

server = BlockingOSCUDPServer(("127.0.0.1", 9997), dispatcher)
server.serve_forever()