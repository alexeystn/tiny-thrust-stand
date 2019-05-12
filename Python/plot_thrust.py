import serial
import numpy as np
from time import sleep, time
from datetime import datetime
from matplotlib import pyplot as plt

serial_port = '/dev/cu.usbserial-A61OXX6Q'

voltage = []
current = []
thrust = []
pwm = []
thrust_offset = 0

current_scale = 0.06 * 22 * 5.0 / 1024  # INA139: Rin * Rout / 1K * Vcc / 2^10bit
voltage_scale = 5.0 / 1024  # Vcc / 2^10bit
thrust_scale = -1/422  # LSB/g, experimental, inverted because thrust is directed upwards

fig, (ax_thrust, ax_current, ax_voltage) = plt.subplots(3, 1, sharex=True, figsize=(8, 6))

graph_thrust = ax_thrust.plot([], thrust, 'b')[0]
graph_current = ax_current.plot([], current, 'r')[0]
graph_voltage = ax_voltage.plot([], voltage, 'g')[0]

ax_thrust.set_title('Thrust, g')
ax_current.set_title('Current, A')
ax_voltage.set_title('Voltage, V')

ax_thrust.set_xlim(0, 200)
ax_thrust.get_xaxis().set_ticks([])

timestamp = time()
filename = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S.txt')

with serial.Serial(serial_port, 115200, timeout=3) as ser:
    with open(filename, 'w') as file:
        sleep(2)
        ser.write(b'S\r\n')
        while True:
            line = ser.readline().decode()
            if line.startswith('Done'):
                break
            file.write(line)
            d = [int(a) for a in line.split()]

            pwm.append(d[0])
            voltage.append(d[1] * voltage_scale)
            current.append(d[2] * current_scale)
            thrust.append(d[3] * thrust_scale)

            graph_thrust.set_ydata(thrust)
            graph_current.set_ydata(current)
            graph_voltage.set_ydata(voltage)

            graph_thrust.set_xdata(range(len(pwm)))
            graph_current.set_xdata(range(len(pwm)))
            graph_voltage.set_xdata(range(len(pwm)))

            ax_thrust.autoscale(enable=True, axis='y', tight=None)
            ax_current.autoscale(enable=True, axis='y', tight=None)
            ax_voltage.autoscale(enable=True, axis='y', tight=None)

            ax_thrust.relim()
            ax_current.relim()
            ax_voltage.relim()

            plt.draw()
            plt.pause(1e-3)
