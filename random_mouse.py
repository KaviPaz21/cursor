"""Move the mouse cursor randomly whenever the user has been idle for a while.

Windows only, no third-party dependencies. No clicking, just movement.
The cursor is handed back immediately as soon as the user touches the mouse
or keyboard. Close the window (or press Ctrl+C) to stop.
"""
import ctypes
import random
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
user32.SetProcessDPIAware()

SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

IDLE_SECONDS = 5            # user inactivity required before we start moving
STEPS = 40                  # smoothness of each move
STEP_DELAY = 0.01           # seconds between steps
PAUSE_RANGE = (0.2, 1.5)    # random pause between moves
POLL_DELAY = 0.2            # how often to check for idleness


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def get_pos():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def idle_seconds():
    """Seconds since the last real user input (SetCursorPos does not count)."""
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(info))
    return (kernel32.GetTickCount() - info.dwTime) / 1000.0


def glide(x1, y1):
    """Move smoothly to (x1, y1). Returns False if the user interfered."""
    x0, y0 = get_pos()
    for i in range(1, STEPS + 1):
        t = i / STEPS
        x, y = int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)
        user32.SetCursorPos(x, y)
        time.sleep(STEP_DELAY)
        # If the cursor isn't where we left it, the user grabbed the mouse.
        if get_pos() != (x, y) or idle_seconds() < IDLE_SECONDS:
            return False
    return True


def main():
    print(f"Random mouse mover running. Idle trigger: {IDLE_SECONDS}s.")
    print("Move the mouse or type to take control. Close this window to stop.")
    try:
        while True:
            if idle_seconds() < IDLE_SECONDS:
                time.sleep(POLL_DELAY)
                continue
            x1 = random.randint(0, SCREEN_W - 1)
            y1 = random.randint(0, SCREEN_H - 1)
            if not glide(x1, y1):
                continue
            time.sleep(random.uniform(*PAUSE_RANGE))
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
