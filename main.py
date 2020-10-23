from bleak import discover
from asyncio import new_event_loop, set_event_loop, get_event_loop
from time import sleep
from binascii import hexlify
from json import dumps
from sys import argv
from datetime import datetime

# Configure update duration (update after n seconds)
UPDATE_DURATION = 10

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
        model="AirPods"+model,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


def run():
    output_file = argv[-1]

    while True:
        data = get_data()

        if data["status"] == 1:
            json_data = dumps(data)
            if len(argv) > 1:
                f = open(output_file, "a")
                f.write(json_data+"\n")
                f.close()
            else:
                print(json_data)

        sleep(UPDATE_DURATION)

if __name__ == '__main__':
    run()


