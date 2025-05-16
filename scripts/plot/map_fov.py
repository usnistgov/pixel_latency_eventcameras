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
import numpy.typing as npt
import argparse
from matplotlib.colors import LinearSegmentedColormap


def parse_args():
    parser = argparse.ArgumentParser("map_fov.py")
    parser.add_argument("output_directory")
    parser.add_argument("-o", "--output", default="out.png")
    parser.add_argument("--vmax", type=int)
    parser.add_argument("--plot-all", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"MAP: OUTPUT = {args.output}, VMAX = {args.vmax}")
    map_filename = args.output_directory + "/map.txt"
    roi_x, roi_y, roi_w, roi_h, maps = parse_map_file(map_filename)
    plot_map(args.output, maps, roi_w, roi_h, args.vmax,
             args.plot_all)


def create_pixel_map(values: list, width: int, height: int) -> npt.NDArray[int]:
    pixels = np.zeros(height * width)

    for i in range(height * width):
        pixels[i] = int(values[i])

    return pixels


def parse_map_file(filename: str) -> (int, int, int, int, dict):
    roi_x, roi_y, roi_w, roi_h = 0, 0, 0, 0
    maps = {0: [], 1: []}

    with open(filename) as file:
        line = file.readline()
        fields = line.split(" ")
        roi_x, roi_y = int(fields[0]), int(fields[1])
        roi_w, roi_h = int(fields[2]), int(fields[3])

        for line in file:
            fields = line.split(" ")
            polarity = int(fields[0])
            map = create_pixel_map(fields[1:], roi_w, roi_h)
            maps[polarity].append(map)

    return roi_x, roi_y, roi_w, roi_h, maps

def plot_polarity(ax: object, maps: dict, roi_w: int, roi_h: int, polarity: int,
                  vmax: int, plot_all: bool):
    print(f"plot polarity {polarity}...")
    mean_map = np.zeros(roi_h * roi_w)
    for idx, map in enumerate(maps[polarity]):
        mean_map += map
        if plot_all:
            ax[polarity, idx].imshow(map.reshape((roi_h, roi_w)), vmin=0, vmax=vmax)

    mean_map /= len(maps[polarity])
    mean_latency = np.mean(mean_map)
    std_latency = np.std(mean_map)
    median_latency = np.median(mean_map)

    print(f"- mean latency = {mean_latency} +- {std_latency}")
    print(f"- median latency = {median_latency}")
    print(f"- min latency = {np.min(mean_map)}")
    print(f"- max latency = {np.max(mean_map)}")

    dead_count = 0
    faulty_pixels = np.zeros(roi_h * roi_w)

    for i, px in enumerate(mean_map):
        row, col = i // roi_w, i % roi_w
        if px < 0:
            dead_count += 1
            faulty_pixels[i] = 1
            print(f"Pixel at (row = {row}, col = {col}) generated no events during the measurment.")
        elif px > (mean_latency + std_latency):
            print(f"Pixel at (row = {row}, col = {col}) as a latency superior to the mean+std ({px} > {mean_latency + std_latency}).")
        elif px > median_latency:
            print(f"Pixel at (row = {row}, col = {col}) as a latency superior to the median ({px} > {median_latency}).")

    print(f"dead pixels: {dead_count} ({dead_count/(roi_w * roi_h)})")

    colors = [(0, "white"), (1, "red")]
    cmap = LinearSegmentedColormap.from_list("falty_pixels", colors)
    ax[polarity, -2].imshow(mean_map.reshape((roi_h, roi_w)), vmax=vmax)
    ax[polarity, -2].set_xlabel("crazy pixels")
    ax[polarity, -1].imshow(faulty_pixels.reshape((roi_h, roi_w)), cmap=cmap)
    ax[polarity, -1].set_xlabel("dead pixels")


def plot_map(output_file: str, maps: dict, roi_w: int, roi_h: int, vmax: int,
             plot_all: bool = False):
    nb_rows = 2
    nb_cols = max(len(maps[0]), len(maps[1])) if plot_all else 0
    fig, ax = plt.subplots(nb_rows, nb_cols + 2, squeeze=False)

    print(f"Number of polarity 0 measurments: {len(maps[0])}")
    print(f"Number of polarity 1 measurments: {len(maps[1])}")

    ax[0, 0].set_ylabel("polarity 0")
    ax[1, 0].set_ylabel("polarity 1")
    fig.suptitle("Single pixel latency map.")

    plot_polarity(ax, maps, roi_w, roi_h, 0, vmax, plot_all)
    plot_polarity(ax, maps, roi_w, roi_h, 1, vmax, plot_all)

    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    if plot_all:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(nb_cols)]
    else:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(2)]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')
    # fig.set_size_inches(8, 6)
    # plt.savefig(output_file, dpi=100)
    plt.show()


if __name__ == "__main__":
    main()
