#!/usr/bin/env python3
"""Private SSH stdin -> ephemeral Linux keyboard/mouse. No event logging."""
import fcntl, os, select, signal, struct, sys, time
EV_KEY, EV_REL, EV_SYN = 1, 2, 0
UI_CREATE, UI_DESTROY, UI_SETUP = 0x5501, 0x5502, 0x405c5503
UI_EVBIT, UI_KEYBIT, UI_RELBIT = 0x40045564, 0x40045565, 0x40045566
EVENT = struct.Struct('@llHHi')
class Device:
    def __init__(self, name, mouse=False):
        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
        self.held = set()
        try:
            fcntl.ioctl(self.fd, UI_EVBIT, EV_KEY)
            for key in (range(272, 277) if mouse else range(1, 256)):
                fcntl.ioctl(self.fd, UI_KEYBIT, key)
            if mouse:
                fcntl.ioctl(self.fd, UI_EVBIT, EV_REL)
                for code in (0, 1, 6, 8): fcntl.ioctl(self.fd, UI_RELBIT, code)
            setup = struct.pack('@HHHH80sI', 0x06, 0, 0, 1, name.encode(), 0)
            fcntl.ioctl(self.fd, UI_SETUP, setup)
            fcntl.ioctl(self.fd, UI_CREATE)
        except BaseException:
            os.close(self.fd)
            raise
    def emit(self, typ, code, value):
        os.write(self.fd, EVENT.pack(0, 0, typ, code, value) + EVENT.pack(0, 0, EV_SYN, 0, 0))
    def key(self, code, value):
        if value and code not in self.held:
            self.emit(EV_KEY, code, 1); self.held.add(code)
        elif not value and code in self.held:
            self.emit(EV_KEY, code, 0); self.held.remove(code)
    def release(self):
        for code in tuple(self.held): self.key(code, 0)
    def close(self):
        try: self.release()
        finally:
            try: fcntl.ioctl(self.fd, UI_DESTROY)
            finally: os.close(self.fd)
def dispatch(line, keyboard, mouse):
    parts = line.split()
    if parts == ['P']: return 'P'
    if parts == ['R']:
        keyboard.release(); mouse.release(); return None
    if len(parts) != 3: raise ValueError('Invalid protocol')
    command, a, b = parts[0], int(parts[1]), int(parts[2])
    if command == 'K' and 1 <= a <= 255 and b in (0, 1): keyboard.key(a, b)
    elif command == 'B' and 272 <= a <= 276 and b in (0, 1): mouse.key(a, b)
    elif command == 'M' and abs(a) <= 4096 and abs(b) <= 4096:
        if a: mouse.emit(EV_REL, 0, a)
        if b: mouse.emit(EV_REL, 1, b)
    elif command == 'W' and abs(a) <= 120 and abs(b) <= 120:
        if a: mouse.emit(EV_REL, 6, a)
        if b: mouse.emit(EV_REL, 8, b)
    else: raise ValueError('Invalid event')
def main():
    keyboard = mouse = None
    def stop(*_): raise SystemExit(0)
    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT): signal.signal(sig, stop)
    try:
        keyboard = Device('MainFrameOS Laptop Keyboard')
        mouse = Device('MainFrameOS Laptop Touchpad', True)
        time.sleep(0.6)  # Allow the compositor to discover both devices.
        print('READY', flush=True)
        buffer = b''
        while True:
            if not select.select([0], [], [], 3)[0]: break
            data = os.read(0, 4096)
            if not data: break
            buffer += data
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                if len(line) > 80: raise ValueError('Oversized event')
                response = dispatch(line.decode('ascii'), keyboard, mouse)
                if response: print(response, flush=True)
            if len(buffer) > 80: raise ValueError('Oversized event')
    finally:
        for device in (mouse, keyboard):
            if device: device.close()
if __name__ == '__main__': main()
