# This server is supposed to take OSC input data from Arduino's
# and relay it to Wekinator and Osculator.
# This server should also provide extra functionality, like
# sending single OSC messages based on Arduino IMU
# data using threshold triggers.

from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

listen_ip = "192.168.8.102"
wekinator_ip = "192.168.8.106"
osculator_ip = "192.168.8.106"
listen_port = 8000
wekinator_port = 8001
osculator_port = 8002

wekinator_address = "/wek/inputs"

osc_wekinator_client = SimpleUDPClient(wekinator_ip, wekinator_port)
osc_osculator_client = SimpleUDPClient(osculator_ip, osculator_port)

prev_args = None

def default_handler(address, *args):
    global prev_args
    # print(f"DEFAULT {address}: {args}")
    osc_wekinator_client.send_message(wekinator_address, args)
    osc_osculator_client.send_message("/raw" + address, args)
    prev_args = args

def manual_unit_handler(address, *args):
    global prev_args

    if (prev_args is not None):
        p, r, y, x, y, z = args
        o_p, o_r, o_y, o_x, o_y, o_z = prev_args

        if (p < 0 and o_p > 0):
            print("Pitch to negative")
            osc_osculator_client.send_message("/p2neg" + address, p)
        elif (p > 0 and o_p < 0):
            print("Pitch to positive")
            osc_osculator_client.send_message("/p2pos" + address, p)
        elif (p < -80 and o_p > -80):
            print("Pitch down")
            osc_osculator_client.send_message("/p2down" + address, p)
        elif (p > 80 and o_p < 80):
            print("Pitch up")
            osc_osculator_client.send_message("/p2up" + address, p)

        if (r < 0 and o_r > 0):
            print("Roll to negative")
            osc_osculator_client.send_message("/r2neg" + address, r)
        elif (r > 0 and o_r < 0):
            print("Roll to positive")
            osc_osculator_client.send_message("/r2pos" + address, r)
        elif (r < -135 and o_r > -135):
            print("Roll left")
            osc_osculator_client.send_message("/r2left" + address, r)
        elif (r > 135 and o_r < 135):
            print("Roll right")
            osc_osculator_client.send_message("/r2right" + address, r)
    
    osc_wekinator_client.send_message(wekinator_address, args)
    osc_osculator_client.send_message("/raw" + address, args)
    prev_args = args

dispatcher = Dispatcher()
dispatcher.map("/ard/0*", manual_unit_handler)
dispatcher.set_default_handler(default_handler)

server = ThreadingOSCUDPServer((listen_ip, listen_port), dispatcher)
print(f"starting server on {listen_ip}:{listen_port}")
server.serve_forever()  # Blocks forever