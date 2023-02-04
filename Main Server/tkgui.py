# This is a utility script designed to be used by mainserver.py
# Provides GUI stuff with Tkinter

import tkinter as tk

window = None
frame = None
outputSettingsWindow = None

# Forward declare updating widgets
inputWidgets = {} # dict to store the pitch, roll and yaw values for each connected board
textlog = None
connectedDevicesList = []

# List of monitor switch buttons
# this is used to turn all of them off except for the selected one,
# because only one board input can be monitored at once
monitorSwitches = []

def Setup(listenTimeout, TimeoutEntryChanged, ButtonListen, ButtonStop, SwitchVisualMonitor):
    global window
    global frame
    global textlog

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
    connectionsLabel.place(x=350, y=0)

    visualizeLabel = tk.Label(master=frame, text="Visualize")
    visualizeLabel.place(x=300, y=20)

    for n in range(3):
        pryLabel = tk.Label(master=frame, text=["Pitch", "Roll", "Heading"][n])
        pryLabel.place(x=500 + 75*n, y=20)

    visualizeTitle = tk.Label(master=frame, text="Visual Orientation Monitor")
    visualizeTitle.place(x=5, y=130)

    startVisButton = tk.Button(master=frame, text="Start Monitor", width=12, height=2, command=lambda: SwitchVisualMonitor(True))
    stopVisButton = tk.Button(master=frame, text="Stop Monitor", width=12, height=2, command=lambda: SwitchVisualMonitor(False))

    startVisButton.place(x=5, y=150)
    stopVisButton.place(x=105, y=150)

def Update():
    window.update()

def AppendPryTexts(sock, boardinput, xOrg, yOrg):
    for n in range(3):
        pryText = tk.Text(master=frame, width=8, height=1)
        pryText.insert("1.0", str(boardinput["pry"[n]]))
        inputWidgets[sock].append(pryText)
        pryText.place(x=xOrg + 75*n, y=yOrg)

def DeselectMonitorSwitches():
    for sw in monitorSwitches:
        sw.deselect()

def LogInsert(index, text):
    index = tk.END if -1 else index
    textlog.insert(index, text)

def LogDelete(start, end):
    end = tk.END if -1 else end
    textlog.delete(start, end)

def LabelInsertAtIndex(indexX, indexY, start, text):
    inputWidgets[indexX][indexY].insert(start, text)

def LabelDeleteAtIndex(indexX, indexY, start, end):
    end = tk.END if -1 else end
    inputWidgets[indexX][indexY].delete(start, end)

def ClearGraphics():
    global connectedDevicesList
    global inputWidgets
    global monitorSwitches

    for dev in connectedDevicesList:
        dev.destroy()

    connectedDevicesList = []

    for sock in inputWidgets.keys():
        for prytext in inputWidgets[sock]:
            prytext.destroy()
    inputWidgets.clear()

    for sw in monitorSwitches:
        sw.destroy()
    monitorSwitches = []

def OpenOutputSettings():
    global outputSettingsWindow

    outputSettingsWindow = tk.Toplevel(frame)
    outputSettingsWindow.geometry("200x200")
    tk.Label(outputSettingsWindow, text="Output Settings").pack()

    outputMethodOptions = [
        "Straight Through",
        "Threshold Pass",
        "Threshold Trigger"
    ]

    clicked = tk.StringVar()
    clicked.set("Method")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *outputMethodOptions).pack()

    messageTypeOptions = [
        "MIDI",
        "OSC"
    ]

    clicked.set("Type")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *messageTypeOptions).pack()

    remappingOptions = [
        "None",
        "0 to 1",
        "-1 to 1",
        "0 to 127"
    ]

    clicked.set("Remapping")
    tk.OptionMenu(outputSettingsWindow, tk.StringVar(), *remappingOptions).pack()


def PlaceLabel(text, x, y):
    label = tk.Label(master=frame, text=text)
    label.place(x=x, y=y)
    connectedDevicesList.append(label)

def AddMonitorSwitch(sock, callback, x, y):
    monitorCheckButton = tk.Checkbutton(master=frame, command=lambda: callback(monitorCheckButton, sock))
    monitorCheckButton.place(x=x, y=y)
    monitorSwitches.append(monitorCheckButton)

def AddSettingsButton(x, y):
    btn = tk.Button(master=frame, command=lambda: OpenOutputSettings(), text="Output", width=8, height=2)
    btn.place(x=x, y=y)