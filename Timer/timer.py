import threading
import time
import os

# Dictionary to hold timers
timers = {
    "timer1": {"duration": 0, "running": False},
    "timer2": {"duration": 0, "running": False},
    "timer3": {"duration": 0, "running": False}
}

# Countdown function
def countdown(timer_id):
    while timers[timer_id]["duration"] > 0 and timers[timer_id]["running"]:
        mins, secs = divmod(timers[timer_id]["duration"], 60)
        os.system("cls" if os.name == "nt" else "clear")  # Clears console
        print(f"[{timer_id}] Time left: {mins:02d}:{secs:02d}")
        time.sleep(1)
        timers[timer_id]["duration"] -= 1

    if timers[timer_id]["duration"] <= 0 and timers[timer_id]["running"]:
        print(f"[{timer_id}] Timer finished!")
    timers[timer_id]["running"] = False

# Start a timer
def start_timer(timer_id, seconds):
    if timer_id not in timers:
        print("Invalid timer ID.")
        return
    timers[timer_id]["duration"] = seconds
    timers[timer_id]["running"] = True
    threading.Thread(target=countdown, args=(timer_id,)).start()
    print(f"{timer_id} started for {seconds} seconds.")

# Stop a timer
def stop_timer(timer_id):
    if timer_id in timers:
        timers[timer_id]["running"] = False
        print(f"{timer_id} stopped.")


# test
# if __name__ == "__main__":
#     # Start all 3 timers with different durations
#     start_timer("timer1", 5)   # 5 seconds
#     start_timer("timer2", 10)  # 10 seconds
#     start_timer("timer3", 7)   # 7 seconds
#     while any(timers[t]["running"] for t in timers):
#         time.sleep(1)
#     print("All timers finished.")

# how to start the timer
#  start_timer(which timer, amout of timer)
