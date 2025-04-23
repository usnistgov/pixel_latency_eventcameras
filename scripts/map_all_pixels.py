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

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import argparse


def parse_args():
    parser = argparse.ArgumentParser("plot")
    parser.add_argument("output_directory")
    parser.add_argument("-W", type=int, default=1280)
    parser.add_argument("-H", type=int, default=720)
    parser.add_argument("--vmax", type=int)
    return parser.parse_args()


def main():
    args = parse_args()
    triggers_filename = args.output_directory + "/triggers.txt"
    positions_filename = args.output_directory + "/positions.txt"

    triggers0, triggers1 = get_triggers(triggers_filename)
    events0, events1 = get_envents(positions_filename)
    plot_map(triggers0, triggers1, events0, events1, args.W, args.H, args.vmax)


def plot_map(triggers0: list, triggers1: list, events0: dict, events1: dict,
             width: int, height: int, vmax: int):
    nb_rows = 2
    nb_cols = max(len(triggers0), len(triggers1))
    fig, ax = plt.subplots(nb_rows, nb_cols + 1, squeeze=False)

    plot_map_polarity(ax, nb_cols, triggers0, events0, 0, width, height, vmax)
    plot_map_polarity(ax, nb_cols, triggers1, events1, 1, width, height, vmax)

    ax[0, 0].set_ylabel("polarity 0")
    ax[1, 0].set_ylabel("polarity 1")
    fig.suptitle("Single pixel latency map.")

    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                 ax=[ax[r, c]
                      for r in range(nb_rows)
                      for c in range(nb_cols)]).set_label('Color Map')
    plt.show()
    # fig.set_size_inches(8, 6)
    # plt.savefig(OUTPUT_FILE, dpi=100)


def plot_map_polarity(ax: object, nb_cols: int, triggers: dict, events:
                      dict, polarity: int, width: int, height: int, vmax: int):
    DEFAULT_PX_VAL=-1
    total = np.zeros((height, width))
    nb_triggers = len(triggers)
    # fill the triggers with the max to get the correct number of figures
    triggers += [max(events.keys()) for _ in range(nb_cols - nb_triggers + 1)]

    for trigger_idx in range(len(triggers) - 1):
        start_timestamp = triggers[trigger_idx]
        end_timestamp = triggers[trigger_idx + 1]
        pixels = np.full((height, width), DEFAULT_PX_VAL)

        for t in range(start_timestamp, end_timestamp):
            delay = t - start_timestamp
            if t in events:
                for x, y in events[t]:
                    if pixels[y, x] == DEFAULT_PX_VAL:
                        pixels[y, x] = delay

        ax[polarity, trigger_idx].imshow(pixels, vmin=0, vmax=vmax)
        ax[polarity, trigger_idx].set_xlabel(f"trigger {trigger_idx}")
        total += pixels ** 2

    nb_images = len(triggers) - 1
    ax[polarity, nb_cols].imshow(np.sqrt(total) / nb_images, vmin=0, vmax=vmax)
    ax[polarity, nb_cols].set_xlabel("total")


def get_triggers(filename: str):
    triggers0 = []
    triggers1 = []
    with open(filename) as file:
        for line in file:
            fields = line.split(" ")
            if int(fields[1]) == 0:
                triggers0.append(int(fields[0]))
            else:
                triggers1.append(int(fields[0]))

    return triggers0, triggers1


def get_envents(filname: str):
    events0 = dict();
    events1 = dict();

    with open(filname) as file:
        line = file.readline()
        while line:
            timestamp = int(line.strip())
            events0[timestamp] = []
            events1[timestamp] = []

            count = int(file.readline().strip())
            for _ in range(count):
                fields = file.readline().strip().split(' ')
                events0[timestamp].append((int(fields[0]), int(fields[1])))

            count = int(file.readline().strip())
            for _ in range(count):
                fields = file.readline().strip().split(' ')
                events1[timestamp].append((int(fields[0]), int(fields[1])))
            line = file.readline()

    return events0, events1


if __name__ == '__main__':
    main()
