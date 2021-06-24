from simplecoremidi import send_midi
from time import sleep

channel = 1
note_on_action = 0x90
velocity = 127

note = 60

while True:
    send_midi((note_on_action | channel, note, velocity))
    sleep(1)
    send_midi((note_on_action | channel, note, 0))
    sleep(1)