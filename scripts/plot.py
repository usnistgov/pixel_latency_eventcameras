#!/usr/bin/env python3

# NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the
# software in any medium, provided that you keep intact this entire notice. You may improve, modify and create
# derivative works of the software or any portion of the software, and you may copy and distribute such modifications
# or works. Modified works should carry a notice stating that you changed the software and should note the date and
# nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the
# source of the software. NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND,
# EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR
# WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE
# CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS
# THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE. You
# are solely responsible for determining the appropriateness of using and distributing the software and you assume
# all risks associated with its use, including but not limited to the risks and costs of program errors, compliance
# with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of
# operation. This software is not intended to be used in any situation where a failure could cause risk of injury or
# damage to property. The software developed by NIST employees is not subject to copyright protection within the
# United States.

# usage
# - display stats:
# ./plot.py output_dir --program=stat
#
# - generate the standard plot (no process) on the given range
# ./plot.py output_dir --program=plot
#
# - generate the average plot on the given range (period size is 50 here)
# ./plot.py output_dir --program=avg,100

import matplotlib.pyplot as plt
import numpy as np
import argparse


def parse_args():
    parser = argparse.ArgumentParser("plot")
    parser.add_argument("output_directory")
    parser.add_argument("-p", "--program", default="plot")
    return parser.parse_args()


def main():
    args = parse_args()
    triggers_filename = args.output_directory + "/triggers.txt"
    counts_filename = args.output_directory + "/counts.txt"
    positions_filename = args.output_directory + "/positions.txt"

    # increase font size
    plt.rcParams.update({"font.size": 20})

    plot_triggers(triggers_filename)
    if args.program == "plot":
        plot(counts_filename)
    else:
        program_args = args.program.split(',')
        program = program_args[0]
        spec = int(program_args[1])

        if program == "avg":
            average_plot(counts_filename, spec)
        elif program == "pos":
            position_plot(positions_filename, spec)


# add the trigger lines on the plot
def plot_triggers(filename: str):
    with open(filename) as file:
        for line in file:
            fields = line.split(" ")
            if int(fields[1]) == 0:
                plt.axvline(int(fields[0]), color='k')
            else:
                plt.axvline(int(fields[0]), color='r')


# Helper function to generate a plot
def make_plot(x, y0, y1, title, xlabel, ylabel):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, wrap=True)
    plt.plot(x, y0, label="polarity 0")
    plt.plot(x, y1, label="polarity 1")
    plt.legend()
    plt.show()


# Plot the number of events on the timestamp
def plot(filename: str):
    x, y0, y1 = [], [], []

    with open(filename) as file:
        for line in file:
            fields = line.split(" ")
            x.append(int(fields[0]))
            y0.append(int(fields[1]))
            y1.append(int(fields[2]))

    make_plot(x, y0, y1,
              f"number of events / timestamp (file = {filename})",
              "timestamp (us)", "number of events")


def position_plot(filname: str, camera_with: int):
    x_0, y_0 = [], []
    x_1, y_1 = [], []

    with open(filname) as file:
        line = file.readline()
        while line:
            timestamp = int(line.strip())
            count = int(file.readline().strip())
            for _ in range(count):
                fields = file.readline().strip().split(' ')
                x_0.append(timestamp)
                y_0.append(int(fields[0]) + int(fields[1])*camera_with)
            count = int(file.readline().strip())
            for _ in range(count):
                fields = file.readline().strip().split(' ')
                x_1.append(timestamp)
                y_1.append(int(fields[0]) + int(fields[1])*camera_with)
            line = file.readline()

    plt.plot(x_0, y_0, marker="o", linestyle="", color="b")
    plt.plot(x_1, y_1, marker="o", linestyle="", color="y")
    plt.title(f"event positions and trigger events over time (ROI = {camera_with}x{camera_with})", wrap=True)
    plt.xlabel("time in us (timestamps of the events)")
    plt.ylabel("position of the event (x + y*roi_width)")

    plt.show()


# Plot the averaged number of events on the given period size for each timestamp
# (the size of the x axis is reduced)
def average_plot(filename: str, period_size: int):
    x, y0, y1 = [], [], []
    result0, result1 = [], []
    period_offset = period_size // 2

    with open(filename) as file:
        for line in file:
            fields = line.split(" ")
            x.append(int(fields[0]))
            y0.append(int(fields[1]))
            y1.append(int(fields[2]))

    # average the values in the roi
    for idx in range(len(x)):
        idx1 = max(0, idx - period_offset)
        idx2 = min(len(x), idx + period_offset)
        result0.append(np.mean(y0[idx1:idx2]))
        result1.append(np.mean(y1[idx1:idx2]))

    # plot_spike_timestamp(x, result1, 30)
    make_plot(x, result0, result1,
              f"average of the number of events (period = {period_size}, file = {filename})",
              "time (us)", "number of events")


# Get the timestamp of each spike in the graph.
# The timestamp is deduced by taking the middle value between the rising and
# falling curve lines at the mean level (use plot=True to display these lines)
def plot_spike_timestamp(x, y, threshold):
    p1, p2 = 0, 0

    for i in range(len(x)):
        if p1 == 0 and p2 == 0 and y[i] >= threshold:
            p1 = x[i]
        elif p1 > 0 and p2 == 0 and y[i] <= threshold:
            p2 = x[i]

        if p1 > 0 and p2 > 0:
            value = (p1 + p2) / 2
            plt.axvline(value)
            p1 = 0
            p2 = 0


if __name__ == '__main__':
    main()
