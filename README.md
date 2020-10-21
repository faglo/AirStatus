# **AirStatus for Linux**
#### Check your AirPods battery level on Linux

#### What is it?
This is a Python 3.6 script, forked from [faglo/AirStatus](https://github.com/faglo/AirStatus) that allows you to check AirPods battery level from your terminal, as JSON output.

### Example output:

```
{"status": 1, "charge": {"left": 90, "right": 90, "case": 50}, "charging": "one", "model": "AirPods Pro"}
```

#### Can I customize it easily?
**Yes, you can!**

You can change the **update frequency** within the main.py file

#### Why percents are displayed in dozens?
This is Apple restrictions, only genius or Apple can fix that :(

#### Used materials
* Some code from [this repo](https://github.com/ohanedan/Airpods-Windows-Service)
* Battery icons from [Icons8](https://icons8.com/icon/set/battery/windows)
