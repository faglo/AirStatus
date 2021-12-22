# **AirStatus for Linux**
#### Check your AirPods battery level on Linux

#### What is it?
This is a Python 3.6 script, forked from [faglo/AirStatus](https://github.com/faglo/AirStatus) that allows you to check AirPods battery level from your terminal, as JSON output.

### Usage

```
python3 main.py [output_file]
```

Output will be stored in `output_file` if specified.

#### Example output

```
{"status": 1, "charge": {"left": 95, "right": 95, "case": -1}, "charging_left": false, "charging_right": false, "charging_case": false, "model": "AirPodsPro", "date": "2021-12-22 11:09:05"}
```

### Installing as a service

Create the file `/etc/systemd/system/airstatus.service` (as root) containing:
```
[Unit]
Description=AirPods Battery Monitor

[Service]
ExecStart=/usr/bin/python3 /PATH/TO/AirStatus/main.py /tmp/airstatus.out
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

Start the service:
```
sudo systemctl start airstatus
```

Enable service on boot:
 ```
sudo systemctl enable airstatus
```

#### Can I customize it easily?
**Yes, you can!**

You can change the **update frequency** within the main.py file

#### Used materials
* Some code from [this repo](https://github.com/ohanedan/Airpods-Windows-Service)
