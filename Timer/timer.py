import threading
import time
import os

# Dictionary to hold timers
timers = {
    "timer1": {"duration": 0, "running": False},
    "timer2": {"duration": 0, "running": False}
}

