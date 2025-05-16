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

import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path
import yaml
import os

# ./plot_latency.py ./no_backlight -m lrb -i 0.01
# ./plot_latency.py ./no_backlight -m lrb -i 0.11
# ./plot_latency.py ./no_backlight -m lrb -i 0.27
# ./plot_latency.py ./no_backlight -m lrb -i 0.48
# ./plot_latency.py ./no_backlight -m lrb -i 0.82

# ./plot_latency.py ./no_backlight -m lri -b max
# ./plot_latency.py ./no_backlight -m lri -b zero
# ./plot_latency.py ./no_backlight -m lri -b min

# ./plot_latency.py ./no_backlight -m lbi -r 630_350_10_10
# ./plot_latency.py ./no_backlight -m lbi -r 640_350_10_10

# ./plot_latency.py ./no_backlight -m lib -r 640_350_10_10

# ./plot_latency.py ./irr0_readout_backlight -m mul --polarity 1
# ./plot_latency.py file1,file2,... -m mul --polarity 1 --logX --logY -std

# ./plot_latency.py ./lens -m map -W 3 -H 3 -M 1000

# configs
BIAS_CONFIGS = dict()
ROI_DIRECTORIES_NAMES = list()
IRRADIANCE_CONFIGS = dict()
MULTI_PIXEL_LATENCY_FILES = dict()

# directories
ROI_DIRECTORIES = list()

VARIDX_TITLE_TABLE = {
    0: "Average latency per ROI",
    1: "Stdev of latency per ROI",
    2: "Min latency per ROI",
    3: "Max of latency per ROI",
    4: "Median latency per ROI",
    5: "Number of 0 events per ROI",
    6: "Number of 1 events per ROI",
}


def create_image(args: object):
    if args.output:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        print("DEBUG: OUTPUT_FILE=", args.output_file)
        plt.savefig(args.output_file, dpi=100)
    else:
        plt.show()


def parse_latency_file(latency_file: str):
    latencies = ([], [])
    stddevs = ([], [])
    min_vals = ([], [])
    max_vals = ([], [])
    median_vals = ([], [])
    nb_zero_vals = ([], [])
    nb_one_vals = ([], [])

    if not Path(latency_file).exists():
        print(f"ERROR: {latency_file} does not exists.")
        return None, None

    with open(latency_file) as latency_file:
        for line in latency_file:
            parts = line.split(';')
            polarity = int(parts[0])
            latency = float(parts[1])
            stddev = float(parts[2])
            if latency == 0 or stddev == 0:
                continue
            latencies[polarity].append(latency)
            stddevs[polarity].append(stddev)

            min_vals[polarity].append(float(parts[3]))
            max_vals[polarity].append(float(parts[4]))
            median_vals[polarity].append(float(parts[5]))
            nb_zero_vals[polarity].append(float(parts[6]))
            nb_one_vals[polarity].append(float(parts[7]))

    if len(latencies[0]) == 1 or len(latencies[1]) == 1:
        #return (latencies[0][0], stddevs[0][0]), (latencies[1][0], stddevs[1][0])
        l0 = (latencies[0][0], stddevs[0][0], float(0), float(0), float(0),
              float(0), float(0))
        l1 = (latencies[1][0], stddevs[1][0], float(0), float(0), float(0),
              float(0), float(0))
        return l0, l1

    l0 = (np.mean(latencies[0]), np.std(latencies[0]), np.mean(min_vals[0]),
          np.mean(max_vals[0]), np.mean(median_vals[0]),
          np.mean(nb_zero_vals[0]), np.mean(nb_one_vals[0]))
    l1 = (np.mean(latencies[1]), np.std(latencies[1]), np.mean(min_vals[1]),
          np.mean(max_vals[1]), np.mean(median_vals[1]),
          np.mean(nb_zero_vals[1]), np.mean(nb_one_vals[1]))
    return l0, l1


# latencies = {
#     irradiance: ([off_latencies_per_bias_config], [on_latencies_per_bias_config])
# }
def get_latencies_irradiance_bias(dir_name: str):
    latencies = {}
    dir = Path(dir_name)

    for irradiance in IRRADIANCE_CONFIGS:
        irradiance_dir = Path(IRRADIANCE_CONFIGS[irradiance])
        latencies[irradiance] = {0: [], 1: []}

        for bias in BIAS_CONFIGS:
            bias_dir = Path(BIAS_CONFIGS[bias])
            l0, l1 = [], []

            for roi_dir in ROI_DIRECTORIES:
                latency_file = dir / irradiance_dir / bias_dir / roi_dir / "latency.txt"
                latency0, latency1 = parse_latency_file(latency_file)
                if latency0 == None or latency1 == None:
                    continue
                l0.append(latency0[0])
                l1.append(latency1[0])

            latencies[irradiance][0].append((np.mean(l0), np.std(l0)))
            latencies[irradiance][1].append((np.mean(l1), np.std(l1)))

    return latencies


# latencies = {
#     roi: ([off_latencies_per_bias_config], [on_latencies_per_bias_config])
# }
def get_latencies_roi_bias(dir_name: str, irradiance_dir_name: str):
    latencies = {}
    irradiance_dir = Path(irradiance_dir_name)
    dir = Path(dir_name)

    for idx, roi_dir in enumerate(ROI_DIRECTORIES):
        latencies[idx] = {0: [], 1: []}

        for bias in BIAS_CONFIGS:
            bias_dir = Path(BIAS_CONFIGS[bias])
            latency_file = dir / irradiance_dir / bias_dir / roi_dir / "latency.txt"
            latency0, latency1 = parse_latency_file(latency_file)
            if latency0 == None or latency1 == None:
                continue
            latencies[idx][0].append(latency0)
            latencies[idx][1].append(latency1)

    return latencies


# latencies = {
#     roi: ([off_latencies_per_irradiance], [on_latencies_per_irradiance])
# }
def get_latencies_roi_irradiance(dir_name: str, bias_dir_name: str):
    latencies = {}
    bias_dir = Path(bias_dir_name)
    dir = Path(dir_name)

    for idx, roi_dir in enumerate(ROI_DIRECTORIES):
        latencies[idx] = {0: [], 1: []}

        for irradiance in IRRADIANCE_CONFIGS:
            irradiance_dir = Path(IRRADIANCE_CONFIGS[irradiance])
            latency_file = dir / irradiance_dir / bias_dir / roi_dir / "latency.txt"
            latency0, latency1 = parse_latency_file(latency_file)
            if latency0 == None or latency1 == None:
                continue
            latencies[idx][0].append(latency0)
            latencies[idx][1].append(latency1)

    return latencies


# latencies = {
#     bias_config: ([off_latencies_per_irradiance], [on_latencies_per_irradiance])
# }
def get_latencies_bias_irradiance(dir_name: str, roi_dir_name: str):
    latencies = {}
    roi_dir = Path(roi_dir_name)
    dir = Path(dir_name)

    for bias in BIAS_CONFIGS:
        bias_dir = Path(BIAS_CONFIGS[bias])
        latencies[bias] = {0: [], 1: []}

        for irradiance in IRRADIANCE_CONFIGS:
            irradiance_dir = Path(IRRADIANCE_CONFIGS[irradiance])
            latency_file = dir / irradiance_dir / bias_dir / roi_dir / "latency.txt"
            latency0, latency1 = parse_latency_file(latency_file)
            if latency0 == None or latency1 == None:
                continue
            latencies[bias][0].append(latency0)
            latencies[bias][1].append(latency1)

    return latencies


def plot_stddev_bias_irr(dir_name: str, args: object):
    vals = []
    for roi_dir in ROI_DIRECTORIES:
        latency_file = Path(dir_name) / IRRADIANCE_CONFIGS[args.irradiance] / BIAS_CONFIGS[
            args.bias] / roi_dir / "latency.txt"
        latency0, latency1 = parse_latency_file(latency_file)
        if latency0 == None or latency1 == None:
            continue
        if args.polarity == "0":
            vals.append(latency0[1])
            plt.title("Latency Stdev per ROI (polarity 0)")
            #print("INFO: Polarity 0 roi_dir=", roi_dir, ", stdev latency=", latency0[1])
        else:
            vals.append(latency1[1])
            plt.title("Latency Stdev per ROI (polarity 1)")
            #print("INFO: Polarity 1 roi_dir=", roi_dir, ", stdev latency=", latency1[1])

    plt.plot(vals)
    plt.ylabel("stdev of latency (us)")
    plt.xlabel("ROI index")
    create_image(args)


'''
Plots min, median, and max values per ROI for each irradiance and each bias
'''

def plot_median_bias_irr(dir_name: str, args: object):
    vals_min = []
    vals_max = []
    vals_median = []
    for roi_dir in ROI_DIRECTORIES:
        latency_file = Path(dir_name) / IRRADIANCE_CONFIGS[args.irradiance] / BIAS_CONFIGS[
            args.bias] / roi_dir / "latency.txt"
        latency0, latency1 = parse_latency_file(latency_file)
        if latency0 == None or latency1 == None:
            continue
        if args.polarity == "0":
            vals_min.append(latency0[2])
            vals_max.append(latency0[3])
            vals_median.append(latency0[4])
            #print("INFO: pol=0 roi_dir=", roi_dir, ", median latency=",latency0[4])
            plt.title("Latency Min/Median/Max per ROI (Polarity 0)")
        else:
            vals_min.append(latency1[2])
            vals_max.append(latency1[3])
            vals_median.append(latency1[4])
            #print("INFO: pol=1 roi_dir=", roi_dir, ", median latency=", latency1[4])
            plt.title("Latency Min/Median/Max per ROI (Polarity 1)")

    # if the parsing did not return average values over 5s exposure then we would have
    # different length of the arrays. The length depends on the number of triggers within 5s.
    min_len = len(vals_min)
    if min_len > len(vals_max):
        print("INFO: length varies:", min_len, ", ", len(vals_max))
        min_len = len(vals_max)

    if min_len > len(vals_median):
        print("INFO: length varies:", min_len, ", ", len(vals_median))
        min_len = len(vals_median)

    plt.plot(vals_min, label="min")
    plt.plot(vals_max, label="max")
    plt.plot(vals_median, label="median")
    plt.legend()
    plt.ylabel("min/median/max of latency (us)")
    plt.xlabel("ROI index")
    create_image(args)


'''
Plots number of 0 and 1 polarity events per ROI for each irradiance and each bias
'''

def plot_nbevents_bias_irr(dir_name: str, args: object):
    vals_nb_zero_pol = []
    vals_nb_one_pol = []
    for roi_dir in ROI_DIRECTORIES:
        latency_file = Path(dir_name) / IRRADIANCE_CONFIGS[args.irradiance] / BIAS_CONFIGS[
            args.bias] / roi_dir / "latency.txt"
        latency0, latency1 = parse_latency_file(latency_file)
        if latency0 == None or latency1 == None:
            continue
        if args.polarity == "0":
            vals_nb_zero_pol.append(latency0[5])
            vals_nb_one_pol.append(latency0[6])
            plt.title(
                "Number of 0 & 1 polarity events per ROI between P0 triggers")
            #print("INFO: Polarity 0 roi_dir=", roi_dir, nb of 0 polarity events=", latency0[5], ", nb of 1 polarity events=", latency0[6])
        else:
            vals_nb_zero_pol.append(latency1[5])
            vals_nb_one_pol.append(latency1[6])
            plt.title(
                "Number of 0 & 1 polarity events per ROI between P1 triggers")
            #print("INFO: Polarity 1 roi_dir=", roi_dir, nb of 0 polarity events=", latency1[5], ", nb of 1 polarity events=", latency1[6])
            #print("INFO: len of latency value array is = ", len(latency1))

    plt.plot(vals_nb_zero_pol, label="nb_pol_0")
    plt.plot(vals_nb_one_pol, label="nb_pol_1")
    plt.legend()
    plt.ylabel("number of 0 & 1 polarity events")
    plt.xlabel("ROI index")
    create_image(args)


def plot_latency(latencies: dict,
                 x: list,
                 stddev: bool,
                 suptitle: str,
                 title: str,
                 xlabel: str,
                 ylabel: str,
                 label=False):
    fig, ax = plt.subplots(2, 1, squeeze=False)
    plt.subplots_adjust(hspace=0.3)

    for k in latencies:
        v = latencies[k]
        latencies0 = [l0[0] for l0 in v[0]]
        latencies0_stddev = [l0[1] for l0 in v[0]]
        latencies1 = [l1[0] for l1 in v[1]]
        latencies1_stddev = [l1[1] for l1 in v[1]]

        if stddev:
            ax[0, 0].errorbar(x, latencies0, latencies0_stddev, label=k)
            ax[1, 0].errorbar(x, latencies1, latencies1_stddev, label=k)
        else:
            ax[0, 0].plot(x, latencies0, marker="o", label=k)
            ax[1, 0].plot(x, latencies1, marker="o", label=k)

    ax[0, 0].set_title(f"Polarity 0 {title}")
    # ax[0, 0].set_xlabel(xlabel)
    ax[0, 0].set_ylabel(ylabel)
    if label:
        ax[0, 0].legend()

    ax[1, 0].set_title(f"Polarity 1 {title}")
    ax[1, 0].set_xlabel(xlabel)
    ax[1, 0].set_ylabel(ylabel)
    if label:
        ax[1, 0].legend()

    fig.suptitle(suptitle)


def plot_latency_roi_bias(latency_directory: str, args: object):
    """Plot latency per ROI over bias configurations."""
    latencies = get_latencies_roi_bias(latency_directory,
                                       IRRADIANCE_CONFIGS[args.irradiance])
    plot_latency(
        latencies, BIAS_CONFIGS.keys(), args.stddev,
        f"Latency for events of polarity 0 and 1 / bias configuration (irradiance = {args.irradiance} W/m2)",
        "event latency per ROI / bias configurations", "bias configurations",
        "latency (us)")
    create_image(args)


def plot_latency_roi_irradiance(latency_directory: str, args: object):
    """Plot latency per ROI over irradiance."""
    latencies = get_latencies_roi_irradiance(latency_directory,
                                             BIAS_CONFIGS[args.bias])
    plot_latency(
        latencies, IRRADIANCE_CONFIGS.keys(), args.stddev,
        f"Latency for events of polarity 0 and 1 / irradiance (bias configuration = {args.bias})",
        "event latency per ROI / irradiance", "irradiance (W/m2)",
        "latency (us)")
    create_image(args)


def plot_latency_bias_irradiance(latency_directory: str, args: object):
    """Plot latency per bias config over irradiance."""
    latencies = get_latencies_bias_irradiance(latency_directory, args.roi)
    plot_latency(latencies, IRRADIANCE_CONFIGS.keys(), args.stddev,
                 "Latency for bias configurations / irradiance",
                 "latency for bias configurations / irradiance",
                 "irradiance (W/m2)", "latency (us)", True)
    plt.legend()
    create_image(args)


def plot_latency_irradiance_bias(latency_directory: str, args: object):
    """Plot latency per irradiance over bias configurations."""
    latencies = get_latencies_irradiance_bias(latency_directory)
    plot_latency(
        latencies, BIAS_CONFIGS.keys(), args.stddev,
        "Latency for events of polarity 0 and 1 per irradiance / bias configuration",
        "event latency per irradiace / bias config", "bias config",
        "latency (us)", True)
    create_image(args)


def plot_map(latency_directory: str, args: object):
    width = int(args.width)
    height = int(args.height)
    vmax = int(args.vmax)
    polarity = int(args.polarity)
    dir = Path(latency_directory)
    fig, ax = plt.subplots(len(IRRADIANCE_CONFIGS.keys()),
                           len(BIAS_CONFIGS.keys()),
                           squeeze=False, sharex=True, sharey=True)
    for irr_idx, irr in enumerate(IRRADIANCE_CONFIGS):
        for bias_idx, bias in enumerate(BIAS_CONFIGS):
            latencies = np.zeros((width, height))
            for roi_idx, roi in enumerate(ROI_DIRECTORIES):
                latency_file = dir / IRRADIANCE_CONFIGS[irr] / \
                    BIAS_CONFIGS[bias] / roi / "latency.txt"
                latency0, latency1 = parse_latency_file(latency_file)
                if latency0 == None or latency1 == None:
                    latencies[roi_idx // height, roi_idx % height] = vmax
                    continue
                if polarity == 0:
                    latencies[roi_idx // height, roi_idx % height] = \
                        latency0[1 if args.stddev else 0]
                else:
                    latencies[roi_idx // height, roi_idx % height] = \
                        latency1[1 if args.stddev else 0]

            ax[irr_idx, bias_idx].imshow(latencies, vmin=0, vmax=vmax)

    for irr_idx, irr in enumerate(IRRADIANCE_CONFIGS):
        ax[irr_idx, 0].set_ylabel(f"{irr}")

    for bias_idx, bias in enumerate(BIAS_CONFIGS):
        ax[len(IRRADIANCE_CONFIGS) - 1, bias_idx].set_xlabel(bias)

    if args.stddev:
        fig.suptitle("Stdev of latency per ROI")
    else:
        fig.suptitle("Average latency per ROI")

    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    ax = [ax[r, c] for r in range(len(ROI_DIRECTORIES.keys()))
          for c in range(len(BIAS_CONFIGS.keys()))]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')

    create_image(args)


'''
Plot maps of avg, stdev, min, max, median, nb of 0 events, nb of 1 events
'''

def plot_map_roi(latency_directory: str, args: object):
    width, height = int(args.width), int(args.height)
    vmax = int(args.vmax)
    varidx = int(args.varidx)
    dir = Path(latency_directory)
    fig, ax = plt.subplots(len(IRRADIANCE_CONFIGS.keys()),
                           len(BIAS_CONFIGS.keys()),
                           squeeze=False,
                           sharex=True,
                           sharey=True)

    if varidx < 0 or varidx >= 7:
        print("ERROR: index of the pre-computed stats is out of range, var=",
              var, ", max len for P0=", str(len(latency0)))
        return

    for irr_idx, irr in enumerate(IRRADIANCE_CONFIGS):
        irr_dir = IRRADIANCE_CONFIGS[irr]
        for bias_idx, bias in enumerate(BIAS_CONFIGS):
            bias_dir = BIAS_CONFIGS[bias]
            latencies = np.zeros((width, height))
            for roi_idx, roi in enumerate(ROI_DIRECTORIES):
                latency_file = dir / irr_dir / bias_dir / roi / "latency.txt"
                latency0, latency1 = parse_latency_file(latency_file)
                if latency0 == None or latency1 == None:
                    latencies[roi_idx // height, roi_idx % height] = vmax
                    continue
                latencies[roi_idx // height, roi_idx % height] = \
                    latency0[varidx] if args.polarity == "0" else latency1[varidx]

            ax[irr_idx, bias_idx].imshow(latencies, vmin=0, vmax=vmax)

    for irr_idx, irr in enumerate(IRRADIANCE_CONFIGS.keys()):
        ax[irr_idx, 0].set_ylabel(f"{irr}")

    for bias_idx, bias in enumerate(BIAS_CONFIGS.keys()):
        ax[len(IRRADIANCE_CONFIGS) - 1, bias_idx].set_xlabel(bias)

    fig.suptitle(VARIDX_TITLE_TABLE[varidx])


    value_min = np.min(latencies)
    value_max = np.max(latencies)
    print("DEBUG: value_min:", value_min, " value_max:", value_max)
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    ax = [ax[r, c] for r in range(len(ROI_DIRECTORIES.keys()))
          for c in range(len(BIAS_CONFIGS.keys()))]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')
    create_image(args)


def plot_multipixel_latency(latency_directory: str, args: object):
    polarity = int(args.polarity)
    latency_directories = latency_directory.split(",")
    results = dict()

    for cam_idx, latency_dir in enumerate(latency_directories):
        result = {}

        with open(Path(latency_dir) / "config.yaml") as config_file:
            config = yaml.safe_load(config_file)
            MULTI_PIXEL_LATENCY_FILES = config["multi_pixel_latency_files"]

        for size in MULTI_PIXEL_LATENCY_FILES.keys():
            dir = Path(MULTI_PIXEL_LATENCY_FILES[size])
            # this code works for ROI size variation but not for irradiance variation
            sub_dir = str(dir)[4:]  # remove roi_
            sub_dir = sub_dir.replace("x", "_")  # replace WxH with W_H values
            print("DEBUG: sub_dir=", sub_dir)
            latency_file = os.path.join(latency_dir, dir, sub_dir, "latency.txt")
            if not Path(latency_file).exists():
                print(f"ERROR: {latency_file} does not exits.")
                continue
            print("DEBUG: latency_dir=", latency_dir, ", dir=", dir, ", latency_file=", latency_file)
            result[int(size)] = parse_latency_file(latency_file)

        results[f"cam {cam_idx}"] = result

    for cam in results.keys():
        result = results[cam]
        values = [latency[polarity][0] for latency in result.values()]
        # coef = np.polyfit(list(result.keys()), values, 1)
        # poly1d = np.poly1d(coef)
        std = [latency[polarity][1] for latency in result.values()]
        print(values)
        if args.stddev:
            plt.errorbar(result.keys(), values, std, label=cam)
        else:
            x = list(result.keys())
            # plt.plot(x, values, x, poly1d(x), '--', label=cam)
            plt.plot(x, values, label=cam)

    plt.ylabel("latency (us)")
    plt.xlabel("nb pixels")
    plt.legend()
    plt.title("Latency over ROI sizes")
    if args.logX:
        plt.xscale("log")
    if args.logY:
        plt.yscale("log")
    create_image(args)


def print_stddev(dir_name: str):
    nb_rois = len(ROI_DIRECTORIES)

    def print_stddev_bias(latencies, irradiance, polarity):
        """Print the mean standard deviation between the ROIs per biases
        configurations at a specific irradiance."""
        values = []
        for bias_idx in range(len(BIAS_CONFIGS.keys())):
            values.append(
                np.std([
                    latencies[roi][polarity][bias_idx][0]
                    for roi in range(nb_rois)
                ]))

        print(
            f"\tPolarity {polarity}: stddev[{irradiance}] = {np.mean(values)}"
            f" (max = {np.max(values)}, min = {np.min(values)})")

    def print_stddev_irradiance(latencies, bias, polarity):
        """Print the mean standar deviation between ROIs per irradiance for a
        given bias config."""
        values = []
        for irr_idx in range(len(IRRADIANCE_CONFIGS.keys())):
            values.append(
                np.std([
                    latencies[roi][polarity][irr_idx][0]
                    for roi in range(nb_rois)
                ]))

        print(f"\tPolarity {polarity}: stddev[{bias}] = {np.mean(values)}"
              f" (max = {np.max(values)}, min = {np.min(values)})")

    for irradiance in IRRADIANCE_CONFIGS.keys():
        # latencies = {
        #     roi: ([off_latencies_per_bias_config], [on_latencies_per_bias_config])
        # }
        latencies = get_latencies_roi_bias(dir_name,
                                           IRRADIANCE_CONFIGS[irradiance])
        print(f"Standard deviation for {irradiance} W/m^2:")
        print_stddev_bias(latencies, irradiance, 0)
        print_stddev_bias(latencies, irradiance, 1)

    for bias_idx, bias in enumerate(BIAS_CONFIGS.keys()):
        # latencies = {
        #     roi: ([off_latencies_per_irradiance], [on_latencies_per_irradiance])
        # }
        latencies = get_latencies_roi_irradiance(dir_name, BIAS_CONFIGS[bias])
        print(f"Standard deviation for {bias}:")
        print_stddev_irradiance(latencies, bias, 0)
        print_stddev_irradiance(latencies, bias, 1)


def parse_args():
    parser = argparse.ArgumentParser("plot_latency")
    parser.add_argument("latency_directory")
    parser.add_argument(
        "-m",
        "--mode",
        help=
        "mode: lrb/lri/lbi/lib/mul/map/std/stdroi (use mode `help` for more information)"
    )
    parser.add_argument("-i", "--irradiance", default=0)
    parser.add_argument("-b",
                        "--bias",
                        default="zero",
                        help="bias config name")
    parser.add_argument("-r",
                        "--roi",
                        default="640_360_10_10",
                        help="roi x_y_w_h")
    parser.add_argument("-std",
                        "--stddev",
                        action="store_true",
                        help="plot the standard deviation using errorbars")
    parser.add_argument("-logX", "--logX", action="store_true",
                        help="use log scale")
    parser.add_argument("-logY", "--logY", action="store_true",
                        help="use log scale")
    parser.add_argument("-P", "--polarity", default=1)
    parser.add_argument("-W", "--width", default=3)
    parser.add_argument("-H", "--height", default=3)
    parser.add_argument("-M", "--vmax", default=1000)
    parser.add_argument("-V", "--varidx", default=0)
    parser.add_argument("-O", "--output", action='store_true', required=False)
    parser.add_argument("-o", "--output-file", default="./test.png",
                        required=False)

    return parser.parse_args()


def main():
    args = parse_args()
    plt.rcParams.update({'font.size': 20})

    global BIAS_CONFIGS
    global ROI_DIRECTORIES_NAMES
    global IRRADIANCE_CONFIGS
    global MULTI_PIXEL_LATENCY_FILES
    global ROI_DIRECTORIES

    if args.output:
        plt.rcParams.update({'font.size': 13})
    print("DEBUG: OUTPUT_FLAG= ", args.output, ", OUTPUT_FILE=", args.output_file)

    with open(Path(args.latency_directory.split(",")[0]) / "config.yaml") as config_file:
        config = yaml.safe_load(config_file)
        BIAS_CONFIGS = config["bias_configs"]
        ROI_DIRECTORIES_NAMES = config["roi_directories_names"]
        IRRADIANCE_CONFIGS = config["irradiance_configs"]
        MULTI_PIXEL_LATENCY_FILES = config["multi_pixel_latency_files"]
        ROI_DIRECTORIES = [
            Path(directory_name) for directory_name in ROI_DIRECTORIES_NAMES
        ]

    if args.mode == "lrb":
        plot_latency_roi_bias(args.latency_directory, args)
    elif args.mode == "lri":
        plot_latency_roi_irradiance(args.latency_directory, args)
    elif args.mode == "lbi":
        plot_latency_bias_irradiance(args.latency_directory, args)
    elif args.mode == "lib":
        plot_latency_irradiance_bias(args.latency_directory, args)
    elif args.mode == "mul":
        plot_multipixel_latency(args.latency_directory, args)
    elif args.mode == "map":
        plot_map(args.latency_directory, args)
    elif args.mode == "maproi":
        plot_map_roi(args.latency_directory, args)
    elif args.mode == "std":
        plot_stddev_bias_irr(args.latency_directory, args)
    elif args.mode == "median":
        plot_median_bias_irr(args.latency_directory, args)
    elif args.mode == "nbevents":
        plot_nbevents_bias_irr(args.latency_directory, args)
    elif args.mode == "stdroi":
        print_stddev(args.latency_directory)
    else:
        print("""
              Modes documentation:
              - lrb: plot latency per roi over the baises configurations.
                     Requires [--irradiance] and [--stddev] (optional).
              - lri: plot latency per roi over the irradiace.
                     Requires [--bias] and [--stddev] (optional).
              - lbi: plot latency per bias config over the irradiance.
                     Requires [--roi] and [--stddev] (optional).
              - lib: plot latency per irradiance over the biases configurations.
                     Requires [--stddev] (optional).
              - mul: plot multi pixel latency.
              - map: plot latency map.
                     Requires:
                     - [-W]: number of ROIs on the x axis.
                     - [-H]: number of ROIs on the y axis.
                     - [-M]: max latency.
                     - [--stddev] (optional): plot the standard deviation.
              - maproi: plot latency map.
                     Requires:
                     - [-W]: number of ROIs on the x axis.
                     - [-H]: number of ROIs on the y axis.
                     - [-M]: max latency.
                     - [--varidx]: index of a variable.
              - std: plot standard deviation for one bias configuration and one
                     irradiance.
                     Requires [--bias] and [--irradiance]
              - median: plot min/median/max for one bias configuration and one
                     irradiance.
                     Requires [--bias] and [--irradiance]
              - nbevents: plot number of 0 and 1 events for one bias configuration and one
                     irradiance.
                     Requires [--bias] and [--irradiance]
              - stdroi: print standard deviation between roi values.
              """)


if __name__ == "__main__":
    main()
