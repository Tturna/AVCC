# This is a utility script designed to be used by mainserver.py
# Provides GUI stuff with Tkinter

import tkinter as tk

window: tk.Tk
frame: tk.Frame
outputSettingsWindow = None

# Forward declare updating widgets
inputWidgets = {}  # dict to store the pitch, roll and yaw values for each connected board
textlog: tk.Text
connectedDevicesList = []

# List of monitor switch buttons
# this is used to turn all of them off except for the selected one,
# because only one board input can be monitored at once
monitorSwitches = []


def setup(listen_timeout, timeout_entry_changed, listen_callback, stop_callback, switch_visual_monitor):
    global window
    global frame
    global textlog

    window = tk.Tk()
    window.title("AVCC")
    frame = tk.Frame(master=window, width=960, height=270)
    frame.pack()
    listen_title = tk.Label(master=frame, text="Arduino Listener\n")
    listen_title.place(x=5, y=0)
    # ipEntry = tk.Entry(width=15)
    # ipEntry.insert(0, host)
    # ipEntry.bind("<Return>", IPEntryChanged)
    # ipEntry.pack()
    timeout_label = tk.Label(master=frame, text="Listen Timeout")
    timeout_label.place(x=5, y=30)
    timeout_entry = tk.Entry(master=frame, width=10)
    timeout_entry.insert(0, str(listen_timeout))
    timeout_entry.bind("<Return>", lambda event: timeout_entry_changed(event.widget.get()))  # Change to separate button?
    timeout_entry.place(x=5, y=50)
    button_con = tk.Button(master=frame, text="Start Listening", width=12, height=2)
    button_con.bind("<Button-1>", listen_callback)  # When mouse1 is pressed on this widget, run callback
    button_con.place(x=5, y=70)
    button_stop = tk.Button(master=frame, text="Stop Listening", width=12, height=2)
    button_stop.bind("<Button-1>", stop_callback)
    button_stop.place(x=105, y=70)
    textlog = tk.Text(master=frame, width=50, height=1)
    textlog.place(x=0, y=250)

    connections_label = tk.Label(master=frame, text="Connected devices:")
    connections_label.place(x=350, y=0)

    visualize_label = tk.Label(master=frame, text="Visualize")
    visualize_label.place(x=300, y=20)

    for i, v in enumerate(["Pitch", "Roll", "Heading"]):
        pry_label = tk.Label(master=frame, text=v)
        pry_label.place(x=500 + 75 * i, y=20)

    visualize_title = tk.Label(master=frame, text="Visual Orientation Monitor")
    visualize_title.place(x=5, y=130)

    start_vis_button = tk.Button(master=frame, text="Start Monitor", width=12, height=2,
                                 command=lambda: switch_visual_monitor(True))
    stop_vis_button = tk.Button(master=frame, text="Stop Monitor", width=12, height=2,
                                command=lambda: switch_visual_monitor(False))

    start_vis_button.place(x=5, y=150)
    stop_vis_button.place(x=105, y=150)


def update():
    window.update()


def append_pry_texts(sock, board_input, x_org, y_org):
    for n in range(3):
        pry_text = tk.Text(master=frame, width=8, height=1)
        pry_text.insert("1.0", str(board_input["pry"[n]]))
        inputWidgets[sock].append(pry_text)
        pry_text.place(x=x_org + 75 * n, y=y_org)


def deselect_monitor_switches():
    for sw in monitorSwitches:
        sw.deselect()


def log_insert(index, text):
    index = tk.END if -1 else index
    textlog.insert(index, text)


def log_delete(start, end):
    end = tk.END if -1 else end
    textlog.delete(start, end)


def label_insert_at_index(index_x, index_y, start, text):
    inputWidgets[index_x][index_y].insert(start, text)


def label_delete_at_index(index_x, index_y, start, end):
    end = tk.END if -1 else end
    inputWidgets[index_x][index_y].delete(start, end)


def update_input_widget(sock, pry):
    for i, v in enumerate("pry"):
        label_delete_at_index(sock, i, "1.0", -1)
        label_insert_at_index(sock, i, "1.0", str(pry[v]))


def clear_graphics():
    global connectedDevicesList
    global inputWidgets
    global monitorSwitches

    for dev in connectedDevicesList:
        dev.destroy()

    connectedDevicesList = []

    for sock in inputWidgets.keys():
        for pry_text in inputWidgets[sock]:
            pry_text.destroy()
    inputWidgets.clear()

    for sw in monitorSwitches:
        sw.destroy()
    monitorSwitches = []


def open_output_settings():
    global outputSettingsWindow

    outputSettingsWindow = tk.Toplevel(frame)
    outputSettingsWindow.geometry("200x200")
    tk.Label(outputSettingsWindow, text="Output Settings").pack()

    output_method_options = [
        "Straight Through",
        "Threshold Pass",
        "Threshold Trigger"
    ]

    clicked = tk.StringVar()
    clicked.set("Method")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *output_method_options).pack()

    message_type_options = [
        "MIDI",
        "OSC"
    ]

    clicked.set("Type")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *message_type_options).pack()

    remapping_options = [
        "None",
        "0 to 1",
        "-1 to 1",
        "0 to 127"
    ]

    clicked.set("Remapping")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *remapping_options).pack()


def place_label(text, x, y):
    label = tk.Label(master=frame, text=text)
    label.place(x=x, y=y)
    connectedDevicesList.append(label)


def add_monitor_switch(sock, callback, x, y):
    monitor_check_button = tk.Checkbutton(master=frame, command=lambda: callback(monitor_check_button, sock))
    monitor_check_button.place(x=x, y=y)
    monitorSwitches.append(monitor_check_button)


def add_settings_button(x, y):
    btn = tk.Button(master=frame, command=lambda: open_output_settings(), text="Output", width=8, height=2)
    btn.place(x=x, y=y)
