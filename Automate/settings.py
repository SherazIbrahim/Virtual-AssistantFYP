# Handle the config file of the program

import configparser
import os
from datetime import date


CONFIG = configparser.ConfigParser()


# Check the location of the configuration file, default to the home directory
filename = "automate.cfg"
config_location = os.environ.get("APPDATA")
config_location = os.path.join(config_location, filename)



def save_config():
    with open(config_location, "w") as config_file:
        CONFIG.write(config_file)


try:
    with open(config_location) as config_file:
        CONFIG.read(config_location)
except:
    CONFIG["DEFAULT"] = {
        "Repeat Count": 1,
        "Recording Hotkey": "shift+esc",
        "Playback Hotkey": "esc+ctrl",
        "voiceid": 1,
        "musicdir": os.path.join(os.environ['USERPROFILE'],"Music"),
        "mouse_sensibility": 20
    }
