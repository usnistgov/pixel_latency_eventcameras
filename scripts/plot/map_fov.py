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


class MapInfos:
    def __init__(self):
        self.width = 0
        self.height = 0
        # statistics
        ## latency
        self.mean_latency = [0, 0]
        self.std_latency = [0, 0]
        self.median_latency = [0, 0]
        self.min_latency = [0, 0]
        self.max_latency = [0, 0]
        ## event count
        self.mean_count = [0, 0]
        self.std_count = [0, 0]
        self.median_count = [0, 0]
        self.min_count = [0, 0]
        self.max_count = [0, 0]
        # maps parsed from C++ program output files
        self.latency_maps = [[], []]
        self.count_maps = [[], []]
        # statistic maps
        self.mean_latency_map = [None, None]
        self.mean_count_map = [None, None]
        self.frozen_pixels_map = [None, None]
        self.hot_pixels_map = [None, None]
        self.cold_pixels_map = [None, None]


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
    map_infos = parse_map_files(args.output_directory)

    print(f"Number of polarity 0 measurments: {len(map_infos.latency_maps[0])}")
    print(f"Number of polarity 1 measurments: {len(map_infos.latency_maps[1])}")

    plot_latency_map(args.output, map_infos, args.vmax, args.plot_all)
    plot_count_map(args.output, map_infos, args.plot_all)


def create_pixel_map(values: list, width: int, height: int) -> npt.NDArray[int]:
    pixels = np.zeros(height * width)

    for i in range(height * width):
        pixels[i] = int(values[i])

    return pixels


def parse_map_files(output_directory: str) -> MapInfos:
    latency_map_file = output_directory + "/map.txt"
    count_map_file = output_directory + "/count_map.txt"
    map_infos = MapInfos()

    with open(latency_map_file) as file:
        line = file.readline()
        fields = line.split(" ")
        _, _ = int(fields[0]), int(fields[1])
        width, height = int(fields[2]), int(fields[3])
        map_infos.width = width
        map_infos.height = height

        for line in file:
            fields = line.split(" ")
            polarity = int(fields[0])
            map = create_pixel_map(fields[1:], width, height)
            map_infos.latency_maps[polarity].append(map)

    with open(count_map_file) as file:
        line = file.readline()  # skip infos

        for line in file:
            fields = line.split(" ")
            polarity = int(fields[0])
            map = create_pixel_map([c.split(':')[polarity] for c in fields[1:]],
                                   width, height)
            map_infos.count_maps[polarity].append(map)

    return map_infos


###############################################################################
#                                   latency                                   #
###############################################################################

def analyze_latency_maps(map_infos: MapInfos, polarity: int,
                         nb_samples: int = 10):
    mean_map = np.zeros(map_infos.height * map_infos.width)
    map_infos.cold_pixels_map[polarity] = np.zeros((map_infos.height,
                                                   map_infos.width))

    for map in map_infos.latency_maps[polarity][:nb_samples]:
        mean_map += map
        cold_threshold = np.mean(map) * 10
        for i, px in enumerate(map):
            if px > cold_threshold:
                row, col = i // map_infos.width, i % map_infos.width
                map_infos.cold_pixels_map[polarity][row, col] += 1

    size = len(map_infos.latency_maps[polarity][:nb_samples])
    mean_map /= size

    map_infos.mean_latency_map[polarity] = mean_map
    map_infos.mean_latency[polarity] = np.mean(mean_map)
    map_infos.std_latency[polarity] = np.std(mean_map)
    map_infos.median_latency[polarity] = np.median(mean_map)
    map_infos.min_latency[polarity] = np.min(mean_map)
    map_infos.max_latency[polarity] = np.max(mean_map)

    print(f"- mean latency = {map_infos.mean_latency[polarity]} +- {map_infos.std_latency[polarity]}")
    print(f"- median latency = {map_infos.median_latency[polarity]}")
    print(f"- min latency = {map_infos.min_latency[polarity]}")
    print(f"- max latency = {map_infos.max_latency[polarity]}")

    frozen_count = 0
    map_infos.frozen_pixels_map[polarity] = np.zeros((map_infos.height,
                                                      map_infos.width))
    for i, px in enumerate(mean_map):
        row, col = i // map_infos.width, i % map_infos.width
        if px < 0:
            frozen_count += 1
            map_infos.frozen_pixels_map[polarity][row, col] = 1
            print(f"Frozen pixel at (row = {row}, col = {col}).")
        elif map_infos.cold_pixels_map[polarity][row, col] > 0.8 * size:
            print(f"Cold pixels at (row = {row}, col = {col}).")
    frozen_percentage = 100 * frozen_count / (map_infos.width * map_infos.height)
    print(f"Frozen pixels: {frozen_count} ({frozen_percentage})")


def plot_polarity_latency(ax: object, map_infos: MapInfos, polarity: int,
                          vmax: int, plot_all: bool):
    print(f"plot polarity {polarity}...")
    analyze_latency_maps(map_infos, polarity)

    if plot_all:
        for idx, map in enumerate(map_infos.latency_maps):
            ax[idx, 0].imshow(map.reshape((map_infos.height, map_infos.width)),
                              vmin=0, vmax=vmax)

    colors = [(0, "white"), (1, "red")]
    cmap = LinearSegmentedColormap.from_list("falty_pixels", colors)
    ax[polarity, -2].imshow(map_infos
                              .mean_latency_map[polarity]
                              .reshape((map_infos.height, map_infos.width)),
                            vmax=vmax)
    ax[polarity, -2].set_xlabel("Mean Latency")
    ax[polarity, -1].imshow(map_infos.frozen_pixels_map[polarity], cmap=cmap)
    ax[polarity, -1].set_xlabel("Frozen Pixels")


def plot_latency_map(output_file: str, map_infos: MapInfos, vmax: int,
                     plot_all: bool = False):
    nb_rows = 2
    nb_cols = max(len(map_infos.latency_maps[0]),
                  len(map_infos.latency_maps[1])) if plot_all else 0
    fig, ax = plt.subplots(nb_rows, nb_cols + 2, squeeze=False)

    ax[0, 0].set_ylabel("polarity 0")
    ax[1, 0].set_ylabel("polarity 1")
    fig.suptitle("Single pixel latency map.")

    plot_polarity_latency(ax, map_infos, 0, vmax, plot_all)
    plot_polarity_latency(ax, map_infos, 1, vmax, plot_all)

    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis  # plt.cm.RdBu
    if plot_all:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(nb_cols)]
    else:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(2)]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')
    fig.set_size_inches(8, 6)
    plt.savefig("latency-" + output_file, dpi=100)


###############################################################################
#                                   counts                                    #
###############################################################################

def analyze_count_maps(map_infos: MapInfos, polarity: int,
                       nb_samples: int = 10):
    mean_map = np.zeros(map_infos.height * map_infos.width)

    for map in map_infos.count_maps[polarity][:nb_samples]:
        mean_map += map
    mean_map /= len(map_infos.count_maps[polarity][:nb_samples])

    map_infos.mean_count_map[polarity] = mean_map
    map_infos.mean_count[polarity] = np.mean(mean_map)
    map_infos.std_count[polarity] = np.std(mean_map)
    map_infos.median_count[polarity] = np.median(mean_map)
    map_infos.min_count[polarity] = np.min(mean_map)
    map_infos.max_count[polarity] = np.max(mean_map)

    print(f"- mean count = {map_infos.mean_count[polarity]} +- {map_infos.std_count[polarity]}")
    print(f"- median count = {map_infos.median_count[polarity]}")
    print(f"- min count = {map_infos.min_count[polarity]}")
    print(f"- max count = {map_infos.max_count[polarity]}")

    map_infos.hot_pixels_map[polarity] = np.zeros((map_infos.height,
                                                  map_infos.width))
    for i, px in enumerate(mean_map):
        row, col = i // map_infos.width, i % map_infos.width
        if px > (map_infos.median_count[polarity] * 100):
            map_infos.hot_pixels_map[polarity][row, col]
            print(f"Hot pixel at (row = {row}, col = {col}).")


def plot_polarity_count(ax: object, map_infos: MapInfos, polarity: int,
                        plot_all: bool = False):
    print(f"plot polarity {polarity}...")
    analyze_count_maps(map_infos, polarity)

    if plot_all:
        for idx, map in enumerate(map_infos.count_maps):
            ax[idx, 0].imshow(map.reshape((map_infos.height, map_infos.width)))

    colors = [(0, "white"), (1, "red")]
    cmap = LinearSegmentedColormap.from_list("falty_pixels", colors)
    mean_map = map_infos.mean_latency_map[polarity].reshape((map_infos.height,
                                                             map_infos.width))
    ax[polarity, -2].imshow(mean_map)
    ax[polarity, -2].set_xlabel("Mean Count")
    ax[polarity, -1].imshow(map_infos.hot_pixels_map[polarity], cmap = cmap)
    ax[polarity, -1].set_xlabel("Hot Pixels")


def plot_count_map(output_file: str, map_infos: MapInfos, plot_all: bool = False):
    nb_rows = 2
    nb_cols = max(len(map_infos.count_maps[0]),
                  len(map_infos.count_maps[1])) if plot_all else 0
    fig, ax = plt.subplots(nb_rows, nb_cols + 2, squeeze=False)

    ax[0, 0].set_ylabel("polarity 0")
    ax[1, 0].set_ylabel("polarity 1")
    fig.suptitle("Single pixel count map.")

    plot_polarity_count(ax, map_infos, 0, plot_all)
    plot_polarity_count(ax, map_infos, 1, plot_all)

    vmax = max(map_infos.max_count[0], map_infos.max_count[1])
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis  # plt.cm.RdBu
    if plot_all:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(nb_cols)]
    else:
        ax = [ax[r, c] for r in range(nb_rows) for c in range(2)]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')
    fig.set_size_inches(8, 6)
    plt.savefig("count-" + output_file, dpi=100)


if __name__ == "__main__":
    main()
