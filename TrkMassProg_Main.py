import requests
import json
import serial
import time
from datetime import datetime
import os
import subprocess
import multiprocessing
import inquirer
from multiprocessing import Process, Manager
from subprocess import Popen
# import TrkMassProg2_Final_FW as Prog_Final
# from TrkMassProg2_Final_FW import *
# import TrkMassProg2_Low_batt_reset as Prog_Low_batt_rst

if __name__ == '__main__':
    while True:
        q_prog =  [inquirer.List(
                        "Prog",
                        message="Select your Program",
                        choices=["Final FW", "Low Battery Reset"],
                        default=["Final FW"],
                    ),
                ]

        a_prog = inquirer.prompt(q_prog)

        if a_prog["Prog"] == "Final FW":
            subprocess.call("TrkMassProg2_Final_FW.py", shell=True)
        else:
            subprocess.call("TrkMassProg2_Low_batt_reset.py", shell=True)