#!/usr/bin/env -S python3 -u
import sys
import time
import atexit

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

@atexit.register
def cleanup():
    print("Cleanup before exit.")
    GPIO.cleanup()

class Fan:
    def __init__(self, pin, initial_state=0):
        self.pin   = pin
        self.state = initial_state

        GPIO.setup(pin,GPIO.OUT) # make pin into an output

    @property
    def state(self):
        return GPIO.input(self.pin)

    @state.setter
    def state(self, value):
        return GPIO.output(self.pin, value)

    @property
    def enabled(self):
        return self.state == 1

    def on(self):
        self.state = 1

    def off(self):
        self.state = 0

class PWMFan(Fan):
    def __init__(self, pin, initial_state=0, frequency=100):
        self.pin       = pin
        self.frequency = frequency
        self.state     = initial_state

        GPIO.setup(pin,GPIO.OUT) # make pin into an output
        self.pwm       = GPIO.PWM(pin, frequency)
        self.pwm.start(self.dc)

    @property
    def dc(self):
        return self.state * 100
    
    @dc.setter
    def dc(self, value):
        self.pwm.ChangeDutyCycle(value)
        self._state = value / 100

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.dc = value * 100
        return self._state

    @property
    def enabled(self):
        return self.state > 0

class TemperatureController:
    def __init__(self, interval, fan):
        self.interval = interval
        self.fan      = fan

        self.update_temp()
    def read_temp(self):
        with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
            return float(f.read())/1000

    def update_temp(self):
        curr_temp=self.read_temp()
        self.temp=curr_temp

    def loop(self):
        while True:
            self.run()
            time.sleep(self.interval)

    def run(self):
        pass

class SimpleController(TemperatureController):
    def __init__(self, interval, high_temp, low_temp, fan):
        self.high_temp  = high_temp
        self.low_temp   = low_temp

        super().__init__(interval, fan)

    def run(self):
        self.update_temp()
        if not self.fan.enabled and self.temp > self.high_temp: # upper bound to turn on the fan
            self.fan.on()
            print("{} °C - {}: {}%".format(self.temp, 'Fan ON', self.fan.dc))
        elif self.temp < self.low_temp: # lower bound to turn off the fan
            self.fan.off()
            print("{} °C - {}".format(self.temp, 'Fan OFF'))
        else:
            print("{} °C".format(self.temp))

class TableController(TemperatureController):
    def __init__(self, interval, high_temp, low_temp, fan):
        self.high_temp  = high_temp
        self.low_temp   = low_temp

        super().__init__(interval, fan)

    def run(self):
        self.update_temp()
        if not self.fan.enabled and self.temp > self.high_temp: # upper bound to turn on the fan
            self.fan.on()
            print("{} °C - {}: {}%".format(self.temp, 'Fan ON', self.fan.dc))
        elif self.fan.enabled and self.temp < self.low_temp: # lower bound to turn off the fan
            self.fan.off()
            print("{} °C - {}".format(self.temp, 'Fan OFF'))
        else:
            print("{} °C".format(self.temp))

def main():
    fan=PWMFan(17)
    controller = SimpleController(interval=2.0, high_temp=55.0, low_temp=48.0, fan=fan)
    controller.loop()

if __name__ == '__main__':
    main()
