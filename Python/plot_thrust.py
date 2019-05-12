import serial
import numpy as np
from time import sleep, time
from datetime import datetime
from matplotlib import pyplot as plt

serial_port = '/dev/cu.usbserial-A61OXX6Q'

voltage = np.array([])
current = np.array([])
thrust = np.array([])
pwm = np.array([])

current_scale = 0.06 * 22 * 5.0 / 1024  # INA139: Rin * Rout / 1K * Vcc / 2^10bit
voltage_scale = 5.0 / 1024  # Vcc / 2^10bit
thrust_scale = -1/422  # LSB/g, experimental, inverted because thrust is directed upwards

fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 6))
fig.canvas.set_window_title('Tiny Thrust Stand')

graph_thrust = axes[0].plot([], thrust, 'b')[0]
graph_current = axes[1].plot([], current, 'r')[0]
graph_voltage = axes[2].plot([], voltage, 'g')[0]

axes[0].set_title('Thrust, g')
axes[1].set_title('Current, A')
axes[2].set_title('Voltage, V')

axes[0].set_xlim(0, 200)
axes[0].get_xaxis().set_ticks([])

for ax in axes:
    ax.grid()

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

            pwm = np.append(pwm, d[0])
            voltage = np.append(voltage, d[1] * voltage_scale)
            current = np.append(current, d[2] * current_scale)
            thrust = np.append(thrust, d[3] * thrust_scale)
            thrust_offset = np.mean(thrust[pwm == 0])

            graph_thrust.set_ydata(thrust - thrust_offset)
            graph_current.set_ydata(current)
            graph_voltage.set_ydata(voltage)

            x_data = np.arange(0, len(pwm))
            graph_thrust.set_xdata(x_data)
            graph_current.set_xdata(x_data)
            graph_voltage.set_xdata(x_data)

            for ax in axes:
                ax.autoscale(enable=True, axis='y', tight=None)
                ax.relim()

            plt.draw()
            plt.pause(1e-3)
