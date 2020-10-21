from bleak import discover
from PIL import Image
from asyncio import new_event_loop, set_event_loop, get_event_loop
from pystray import Icon, Menu, MenuItem as Item
from multiprocessing import Process
from time import sleep
from binascii import hexlify

# Configure update duration (update after n seconds)
UPDATE_DURATION = 30
# Configure battery level when you get toast notification of discharging
LOW_LEVEL = 20


# Getting data with hex format
async def get_device():
    # Scanning for devices
    devices = await discover()
    for d in devices:
        # Checking for AirPods
        if d.rssi >= -690 and 76 in d.metadata['manufacturer_data']:
            data_hex = hexlify(bytearray(d.metadata['manufacturer_data'][76]))
            data_length = len(hexlify(bytearray(d.metadata['manufacturer_data'][76])))
            if data_length == 54:
                return data_hex
    return False


# Same as get_device() but it's standalone method instead of async
def get_data_hex():
    new_loop = new_event_loop()
    set_event_loop(new_loop)
    loop = get_event_loop()
    a = loop.run_until_complete(get_device())
    return a


# Getting data from hex string and converting it to dict(json)
def get_data():
    raw = get_data_hex()

    # Return blank data if airpods not found
    if not raw:
        return dict(status=0, model="AirPods not found")

    # On 7th position we can get AirPods model, Pro or standard
    if chr(raw[7]) == 'e':
        model = " Pro"
    else:
        model = ""

    # Checking left AirPod for availability and storing charge in variable
    try:
        left = int(chr(raw[12])) * 10
    except ValueError:
        left = -1

    # Checking right AirPod for availability and storing charge in variable
    try:
        right = int(chr(raw[13])) * 10
    except ValueError:
        right = -1

    # Checking AirPods case for availability and storing charge in variable
    try:
        case = int(chr(raw[15])) * 10
    except ValueError:
        case = -1

    # On 14th position we can get charge status of AirPods, I found it with some tests :)
    charge_raw = chr(raw[14])
    if charge_raw == "a":
        charging = "one"
    elif charge_raw == "b":
        charging = "both"
    else:
        charging = "N/A"

    # Return result info in dict format
    return dict(
        status=1,
        charge=dict(
            left=left,
            right=right,
            case=case
        ),
        charging=charging,
        model="AirPods"+model
    )


# Checking AirPods availability and create icon in tray
def create_icon(status, left, right, case, model):
    # Rewriting data dict because cant pass all dict with multiprocessing lib
    data = dict(
        status=status,
        charge=dict(
            left=left,
            right=right,
            case=case
        ),
        model=model
    )
    # Blank values
    a_left = True
    a_right = True
    a_case = True
    charges = dict(
        left=-1,
        right=-1,
        case=-1
    )

    if data["status"] == 0:
        # Setting false availability for all devices and setting icon path
        a_left = False
        a_right = False
        a_case = False
        image = "./icons/no.png"
    else:
        # Checking for availability and errors for connected devices
        charges = data["charge"]
        if charges["left"] == -1 or charges["left"] == 150:
            a_left = False
        if charges["right"] == -1 or charges["right"] == 150:
            a_right = False
        if charges["case"] == -1:
            a_case = False

    # Right click menu
    menu = Menu(
        Item(
            text=data["model"],
            action="",
            enabled=False
        ),
        Item(
            text="Left: {}%".format(charges["left"]),
            action="",
            enabled=False,
            visible=a_left
        ),
        Item(
            text="Right: {}%".format(charges["right"]),
            action="",
            enabled=False,
            visible=a_right
        ),
        Item(
            text="Case: {}%".format(charges["case"]),
            action="",
            enabled=False,
            visible=a_case
        )
    )

    # Selecting lowest charge level for comparing and icon select
    if a_left and charges["left"] > charges["right"]:
        lowest = charges["left"]
    elif a_right and charges["right"] > charges["left"]:
        lowest = charges["right"]
    elif charges["right"] == charges["left"]:
        lowest = charges["right"]
    else:
        lowest = -1

    # Selecting icon for charge levels
    if lowest == -1:
        image = "./icons/no.png"
    elif lowest < 20:
        image = "./icons/empty.png"
    elif lowest < 40:
        image = "./icons/low.png"
    elif lowest < 60:
        image = "./icons/middle.png"
    elif lowest < 80:
        image = "./icons/much.png"
    elif lowest < 100:
        image = "./icons/full.png"
    else:
        image = "./icons/no.png"

    # Creating icon
    Icon(data["model"], Image.open(image), menu=menu).run()

def run():
    data = get_data()
    connected = True
    cache = None
    cached_process = None

    while True:
        if data["status"] == 1:
            # Checking cache and current data for avoid Windows duplicate tray icon bug
            if cache != data["charge"] or not connected:
                # Flushing process(tray icon) and handling error that might be on start
                try:
                    cached_process.terminate()
                except AttributeError:
                    pass

                # Starting new thread(process)
                proc = Process(target=create_icon, args=(1,
                                                         data["charge"]["left"],
                                                         data["charge"]["right"],
                                                         data["charge"]["case"],
                                                         data["model"]))
                proc.start()

                # Setting cache vars
                cached_process = proc
                cache = data["charge"]

        elif data["status"] == 0:
            # Checking cache and current data for avoid Windows duplicate tray icon bug
            if connected:
                # Flushing process(tray icon) and handling error that might be on start
                try:
                    cached_process.terminate()
                except AttributeError:
                    pass
                # Creating process and setting cache var
                proc = Process(target=create_icon, args=(0, -1, -1, -1, data["model"]))
                connected = False
                proc.start()

        sleep(UPDATE_DURATION)


if __name__ == '__main__':
    run()


