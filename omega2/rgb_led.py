# -*- coding: utf-8 -*-

from os import uname
from socket import gethostname
from time import sleep
import sys
import cloud4rpi
import omega2

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'
DATA_SENDING_INTERVAL = 30  # seconds

o2 = omega2.Omega2()


def RGB_init():
    for _, pin in o2.RGB_pins.items():
        o2.gpio_dir_out_1(pin)  # HIGH = OFF


def RED_control(state):
    pin = o2.RGB_pins['R']
    if o2.gpio_set(pin, not state):
        return not o2.gpio_get(pin)


def GREEN_control(state):
    pin = o2.RGB_pins['G']
    if o2.gpio_set(pin, not state):
        return not o2.gpio_get(pin)


def BLUE_control(state):
    pin = o2.RGB_pins['B']
    if o2.gpio_set(pin, not state):
        return not o2.gpio_get(pin)


def main():
    RGB_init()

    # Put variable declarations here
    variables = {
        'Omega LED': {
            'type': 'bool',
            'value': False,
            'bind': o2.led_control
        },
        'RGB LED - Red': {
            'type': 'bool',
            'value': False,
            'bind': RED_control
        },
        'RGB LED - Green': {
            'type': 'bool',
            'value': False,
            'bind': GREEN_control
        },
        'RGB LED - Blue': {
            'type': 'bool',
            'value': False,
            'bind': BLUE_control
        }
    }

    # Put system data declarations here
    diagnostics = {
        'Host': gethostname(),
        'Operating System': " ".join(uname()),
        'Omega2 version': 'Omega2 Plus' if 'p' in o2.version else 'Omega2'
    }

    device = cloud4rpi.Device()
    device.declare(variables)
    device.declare_diag(diagnostics)

    api = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    api.on_command = device.handle_mqtt_commands(api)
    cfg = device.read_config()
    api.publish_config(cfg)

    # Adds a 1 second delay to ensure device variables are created
    sleep(1)

    try:
        diag = device.read_diag()
        api.publish_diag(diag)
        while True:
            data = device.read_data()
            api.publish_data(data)
            sleep(DATA_SENDING_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')
        sys.exit(0)

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])
        sys.exit(1)


if __name__ == '__main__':
    main()
