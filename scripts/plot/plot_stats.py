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

# ./plot_stats.py ./no_backlight -m lrb -i 0.01
# ./plot_stats.py ./no_backlight -m lrb -i 0.11
# ./plot_stats.py ./no_backlight -m lrb -i 0.27
# ./plot_stats.py ./no_backlight -m lrb -i 0.48
# ./plot_stats.py ./no_backlight -m lrb -i 0.82

# ./plot_stats.py ./no_backlight -m lri -b max
# ./plot_stats.py ./no_backlight -m lri -b zero
# ./plot_stats.py ./no_backlight -m lri -b min

# ./plot_stats.py ./no_backlight -m lbi -r 630_350_10_10
# ./plot_stats.py ./no_backlight -m lbi -r 640_350_10_10

# ./plot_stats.py ./no_backlight -m lib -r 640_350_10_10

# ./plot_stats.py ./irr0_readout_backlight -m mul --polarity 1
# ./plot_stats.py file1,file2,... -m mul --polarity 1 --logX --logY -std

# ./plot_stats.py ./lens -m lmap -W 3 -H 3 -M 1000

import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path
import yaml
import os
from parse import Stat, parse_latency_file, parse_count_file

HELP_MESSAGE = """
Modes documentation:
- lrb/crb: plot latency / count per roi over the baises configurations.
           Requires [--irradiance] and [--stddev] (optional).
- lri/cri: plot latency / count per roi over the irradiace.
           Requires [--bias] and [--stddev] (optional).
- lbi/cbi: plot latency / count per bias config over the irradiance.
           Requires [--roi] and [--stddev] (optional).
- lib/cib: plot latency / count per irradiance over the biases configurations.
           Requires [--stddev] (optional).
- lmap/cmap: plot latency / count map.
       Requires:
       - [-W]: number of ROIs on the x axis.
       - [-H]: number of ROIs on the y axis.
       - [-M]: max expected latency / count.
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
"""


VARIDX_TITLE_TABLE = {
    0: "Average latency per ROI",
    1: "Stdev of latency per ROI",
    2: "Min latency per ROI",
    3: "Max of latency per ROI",
    4: "Median latency per ROI",
    5: "Number of 0 events per ROI",
    6: "Number of 1 events per ROI",
}


class Config:
    def __init__(self, result_dir_name):
        self.result_dir = Path(result_dir_name)
        with open(self.result_dir / "config.yaml") as config_file:
            config = yaml.safe_load(config_file)
            self.bias = config["bias_configs"]
            self.irradiance = config["irradiance_configs"]
            self.roi = config["roi_directories_names"]


    def irradiances(self):
        for irr in self.irradiance:
            yield irr, Path(self.irradiance[irr])


    def biases(self):
        for bias in self.bias:
            yield bias, Path(self.bias[bias])


    def rois(self):
        for roi_dir_name in self.roi:
            yield roi_dir_name, Path(roi_dir_name)


###############################################################################
#                                collect data                                 #
###############################################################################


def collect_latency_data(config: Config) -> dict:
    data = dict()

    # parse irradiance measurements
    for irr, irr_dir in config.irradiances():
        data[irr] = dict()
        for bias, bias_dir in config.biases():
            data[irr][bias] = dict()
            for roi, roi_dir in config.rois():
                data[irr][bias][roi] = dict()
                # get latency stats
                latency_file = config.result_dir / irr_dir / bias_dir / roi_dir / "latency.txt"
                stats = parse_latency_file(latency_file)
                if stats != None:
                    data[irr][bias][roi]["latency"] = stats

                # get event rate stats
                count_file = config.result_dir / irr_dir / bias_dir / roi_dir / "count.txt"
                stats = parse_count_file(count_file)
                if stats != None:
                    data[irr][bias][roi]["count"] = stats

    return data


###############################################################################
#                              helper functions                                #
###############################################################################

def create_image(args: object):
    if args.output != "":
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        print("DEBUG: OUTPUT=", args.output)
        plt.savefig(args.output, dpi=100)
    else:
        plt.show()


def plot_stats(latencies: dict,
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
        latencies0 = [l0.mean for l0 in v[0]]
        latencies0_stddev = [l0.stddev for l0 in v[0]]
        latencies1 = [l1.mean for l1 in v[1]]
        latencies1_stddev = [l1.stddev for l1 in v[1]]

        if stddev:
            ax[0, 0].errorbar(x, latencies0, latencies0_stddev, label=k)
            ax[1, 0].errorbar(x, latencies1, latencies1_stddev, label=k)
        else:
            ax[0, 0].plot(x, latencies0, marker="o", label=k)
            ax[1, 0].plot(x, latencies1, marker="o", label=k)

    ax[0, 0].set_title(f"Polarity 0 {title}")
    ax[0, 0].set_ylabel(ylabel)

    ax[1, 0].set_title(f"Polarity 1 {title}")
    ax[1, 0].set_xlabel(xlabel)
    ax[1, 0].set_ylabel(ylabel)

    if label:
        ax[0, 0].legend()
        ax[1, 0].legend()

    fig.suptitle(suptitle)


###############################################################################
#                               data selection                                #
###############################################################################

# stats = {
#     roi: ([off_stat_per_bias_config], [on_stat_per_bias_config])
# }
def get_stat_roi_bias(config: Config,
                      data: dict,
                      stat: str,
                      irradiance_config: str
                      ) -> dict:
    stats = {}

    for idx, roi in enumerate(config.roi):
        stats[idx] = {0: [], 1: []}
        for bias in config.bias:
            stat0, stat1 = data[irradiance_config][bias][roi][stat]
            stats[idx][0].append(stat0)
            stats[idx][1].append(stat1)

    return stats


# stats = {
#     roi: ([off_stat_per_irradiance], [on_stat_per_irradiance])
# }
def get_stat_roi_irradiance(config: Config,
                            data: dict,
                            stat: str,
                            bias_config: str
                            ) -> dict:
    stats = {}

    for idx, roi in enumerate(config.roi):
        stats[idx] = {0: [], 1: []}
        for irr in config.irradiance:
            stat0, stat1 = data[irr][bias_config][roi][stat]
            stats[idx][0].append(stat0)
            stats[idx][1].append(stat1)

    return stats


# stats = {
#     bias_config: ([off_stat_per_irradiance], [on_stat_per_irradiance])
# }
def get_stat_bias_irradiance(config: Config,
                             data: dict,
                             stat: str,
                             roi_config: str) -> dict:
    latencies = {}

    for bias in config.bias:
        latencies[bias] = {0: [], 1: []}
        for irr in config.irradiance:
            stat0, stat1 = data[irr][bias][roi_config][stat]
            latencies[bias][0].append(stat0)
            latencies[bias][1].append(stat1)

    return latencies


# stats = {
#     irradiance: ([off_stat_per_bias_config], [on_stat_per_bias_config])
# }
def get_stat_irradiance_bias(config: Config, data: dict, stat: str) -> dict:
    stats = {}

    for irr in config.irradiance:
        stats[irr] = ([], [])
        for bias in config.bias:
            l0, l1 = [], []
            for roi in config.roi:
                stat0, stat1 = data[irr][bias][roi][stat]
                l0.append(stat0.mean)
                l1.append(stat1.mean)

            stats[irr][0].append(Stat(0, np.mean(l0), np.std(l0)))
            stats[irr][1].append(Stat(0, np.mean(l1), np.std(l1)))

    return stats


###############################################################################
#                               plot latency                                  #
###############################################################################

def plot_latency_roi_bias(config: Config, data: dict, args: object):
    """Plot latency per ROI over bias configurations."""
    latencies = get_stat_roi_bias(config, data, "latency", args.irradiance)
    plot_stats(
        latencies, config.bias.keys(), args.stddev,
        f"Latency for events of polarity 0 and 1 / bias configuration (irradiance = {args.irradiance} W/m2)",
        "event latency per ROI / bias configurations", "bias configurations",
        "latency (us)")
    create_image(args)


def plot_latency_roi_irradiance(config: Config, data: dict, args: object):
    """Plot latency per ROI over irradiance."""
    latencies = get_stat_roi_irradiance(config, data, "latency", args.bias)
    plot_stats(
        latencies, config.irradiance.keys(), args.stddev,
        f"Latency for events of polarity 0 and 1 / irradiance (bias configuration = {args.bias})",
        "event latency per ROI / irradiance", "irradiance (W/m2)",
        "latency (us)")
    create_image(args)


def plot_latency_bias_irradiance(config: Config, data: dict, args: object):
    """Plot latency per bias config over irradiance."""
    latencies = get_stat_bias_irradiance(config, data, "latency", args.roi)
    plot_stats(latencies, config.irradiance.keys(), args.stddev,
                 "Latency for bias configurations / irradiance",
                 "latency for bias configurations / irradiance",
                 "irradiance (W/m2)", "latency (us)", True)
    plt.legend()
    create_image(args)


def plot_latency_irradiance_bias(config: Config, data: dict , args: object):
    """Plot latency per irradiance over bias configurations."""
    latencies = get_stat_irradiance_bias(config,  data, "latency")
    plot_stats(
        latencies, config.bias.keys(), args.stddev,
        "Latency for events of polarity 0 and 1 per irradiance / bias configuration",
        "event latency per irradiace / bias config", "bias config",
        "latency (us)", True)
    create_image(args)


###############################################################################
#                              plot event count                               #
###############################################################################

def plot_count_roi_bias(config: Config, data: dict, args: object):
    """Plot event count per ROI over bias configurations."""
    counts = get_stat_roi_bias(config, data, "count", args.irradiance)
    plot_stats(
        counts, config.bias.keys(), args.stddev,
        f"Event count for polarity 0 and 1 / bias configuration (irradiance = {args.irradiance} W/m2)",
        "event count per ROI / bias configurations", "bias configurations",
        "count (us)")
    create_image(args)


def plot_count_roi_irradiance(config: Config, data: dict, args: object):
    """Plot event count per ROI over irradiance."""
    counts = get_stat_roi_irradiance(config, data, "count", args.bias)
    plot_stats(
        counts, config.irradiance.keys(), args.stddev,
        f"Event count for polarity 0 and 1 / irradiance (bias configuration = {args.bias})",
        "event count per ROI / irradiance", "irradiance (W/m2)",
        "count (us)")
    create_image(args)


def plot_count_bias_irradiance(config: Config, data: dict, args: object):
    """Plot event count per bias config over irradiance."""
    counts = get_stat_bias_irradiance(config, data, "count", args.roi)
    plot_stats(counts, config.irradiance.keys(), args.stddev,
                 "Latency for bias configurations / irradiance",
                 "count for bias configurations / irradiance",
                 "irradiance (W/m2)", "count (us)", True)
    plt.legend()
    create_image(args)


def plot_count_irradiance_bias(config: Config, data: dict , args: object):
    """Plot event count per irradiance over bias configurations."""
    counts = get_stat_irradiance_bias(config, data, "count")
    plot_stats(
        counts, config.bias.keys(), args.stddev,
        "Event count for polarity 0 and 1 per irradiance / bias configuration",
        "event count per irradiace / bias config", "bias config",
        "count (us)", True)
    create_image(args)


###############################################################################
#                            plot other components                             #
###############################################################################

def plot_stddev_bias_irr(config: Config, data: dict, args: object):
    vals = []

    for roi in config.roi:
        stat0, stat1 = data[args.irradiance][args.bias][roi]["latency"]
        stat = stat0 if args.polarity == "0" else stat1
        vals.append(stat.stddev)
        plt.title(f"Latency Stdev per ROI (polarity {args.polarity})")

    plt.plot(vals)
    plt.ylabel("stdev of latency (us)")
    plt.xlabel("ROI index")
    create_image(args)


'''
Plots min, median, and max values per ROI for each irradiance and each bias
'''

def plot_median_bias_irr(config: Config, data: dict, args: object):
    vals_min = []
    vals_max = []
    vals_median = []

    for roi in config.roi:
        stat0, stat1 = data[args.irradiance][args.bias][roi]["latency"]
        stat = stat0 if args.polarity == "0" else stat1
        vals_min.append(stat.min)
        vals_max.append(stat.max)
        vals_median.append(stat.median)
        plt.title(f"Latency Min/Median/Max per ROI (Polarity {args.polarity})")

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

def plot_nbevents_bias_irr(config: Config, data: dict, args: object):
    vals_nb_zero_pol = []
    vals_nb_one_pol = []

    for roi in config.roi:
        stat0, stat1 = data[args.irradiance][args.bias][roi]["latency"]
        stat = stat0 if args.polarity == "0" else stat1
        vals_nb_zero_pol.append(stat.nb0)
        vals_nb_one_pol.append(stat.nb1)
        plt.title(
            f"Number of 0 & 1 polarity events per ROI between P{args.polarity} triggers")

    plt.plot(vals_nb_zero_pol, label="nb_pol_0")
    plt.plot(vals_nb_one_pol, label="nb_pol_1")
    plt.legend()
    plt.ylabel("number of 0 & 1 polarity events")
    plt.xlabel("ROI index")
    create_image(args)


###############################################################################
#                                    maps                                     #
###############################################################################

def plot_map(config: Config, data: dict, stat: str, args: object):
    width, height = int(args.width), int(args.height)
    vmax = int(args.vmax)
    polarity = int(args.polarity)
    fig, ax = plt.subplots(len(config.irradiance),
                           len(config.bias),
                           squeeze=False, sharex=True, sharey=True)

    for irr_idx, irr in enumerate(config.irradiance):
        for bias_idx, bias in enumerate(config.bias):
            latencies = np.zeros((width, height))
            for roi_idx, roi in enumerate(config.roi):
                stat0, stat1 = data[irr][bias][roi][stat]
                stat_ = stat0 if polarity == 0 else stat1
                latencies[roi_idx // height, roi_idx % height] = \
                    stat_.stddev if args.stddev else stat_.mean

            ax[irr_idx, bias_idx].imshow(latencies, vmin=0, vmax=vmax)

    for irr_idx, irr in enumerate(config.irradiance):
        ax[irr_idx, 0].set_ylabel(f"{irr}")

    for bias_idx, bias in enumerate(config.bias):
        ax[len(config.irradiance) - 1, bias_idx].set_xlabel(bias)

    fig.suptitle(f"{'Stdev' if args.stddev else 'Average'} of latency per ROI")

    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    ax = [ax[r, c] for r in range(len(config.irradiance)) for c in range(len(config.bias))]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')

    create_image(args)


'''
Plot maps of avg, stdev, min, max, median, nb of 0 events, nb of 1 events
'''

def plot_map_roi(config: Config, data: dict, args: object):
    width, height = int(args.width), int(args.height)
    vmax = int(args.vmax)
    varidx = int(args.varidx)
    polarity = int(args.polarity)
    fig, ax = plt.subplots(len(config.irradiance.keys()),
                           len(config.bias.keys()),
                           squeeze=False,
                           sharex=True,
                           sharey=True)

    if varidx < 0 or varidx > 7:
        print("ERROR: index of the pre-computed stats is out of range, var=",
              var, ", max len for P0=", str(len(latency0)))
        return

    for irr_idx, irr in enumerate(config.irradiance):
        for bias_idx, bias in enumerate(config.bias):
            latencies = np.zeros((width, height))
            for roi_idx, roi in enumerate(config.roi):
                stat0, stat1 = data[irr][bias][roi]["latency"]
                stat = stat0 if polarity == 0 else stat1
                latencies[roi_idx // height, roi_idx % height] = stat.get(varidx)

            ax[irr_idx, bias_idx].imshow(latencies, vmin=0, vmax=vmax)

    for irr_idx, irr in enumerate(config.irradiance.keys()):
        ax[irr_idx, 0].set_ylabel(f"{irr}")

    for bias_idx, bias in enumerate(config.bias.keys()):
        ax[len(config.irradiance) - 1, bias_idx].set_xlabel(bias)

    fig.suptitle(VARIDX_TITLE_TABLE[varidx])

    value_min = np.min(latencies)
    value_max = np.max(latencies)
    print("DEBUG: value_min:", value_min, " value_max:", value_max)
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.cm.viridis #plt.cm.RdBu
    ax = [ax[r, c] for r in range(len(config.irradiance)) for c in range(len(config.bias))]
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax).set_label('Color Map')
    create_image(args)


def print_stddev(dir_name: str):
    nb_rois = len(config.roi)

    def print_stddev_bias(latencies, irradiance, polarity):
        """Print the mean standard deviation between the ROIs per biases
        configurations at a specific irradiance."""
        values = []
        for bias_idx in range(len(config.bias.keys())):
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
        for irr_idx in range(len(config.irradiance.keys())):
            values.append(
                np.std([
                    latencies[roi][polarity][irr_idx][0]
                    for roi in range(nb_rois)
                ]))

        print(f"\tPolarity {polarity}: stddev[{bias}] = {np.mean(values)}"
              f" (max = {np.max(values)}, min = {np.min(values)})")

    for irradiance in config.irradiance.keys():
        # latencies = {
        #     roi: ([off_latencies_per_bias_config], [on_latencies_per_bias_config])
        # }
        latencies = get_stat_roi_bias(dir_name,
                                           config.irradiance[irradiance])
        print(f"Standard deviation for {irradiance} W/m^2:")
        print_stddev_bias(latencies, irradiance, 0)
        print_stddev_bias(latencies, irradiance, 1)

    for bias_idx, bias in enumerate(config.bias.keys()):
        # latencies = {
        #     roi: ([off_latencies_per_irradiance], [on_latencies_per_irradiance])
        # }
        latencies = get_stat_roi_irradiance(dir_name, "latency", config.bias[bias])
        print(f"Standard deviation for {bias}:")
        print_stddev_irradiance(latencies, bias, 0)
        print_stddev_irradiance(latencies, bias, 1)


###############################################################################
#                                 parse args                                  #
###############################################################################

def parse_args():
    parser = argparse.ArgumentParser("plot_stats")
    parser.add_argument("latency_directory")
    parser.add_argument(
        "-m",
        "--mode",
        help=
        "mode: lrb/lri/lbi/lib/map/std/stdroi (use mode `help` for more information)"
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
    parser.add_argument("-o", "--output", default="",
                        required=False)

    return parser.parse_args()


###############################################################################
#                                    main                                     #
###############################################################################

def select_mode(config: Config, data: dict, args: object):
    match args.mode:
        case "lrb":
            plot_latency_roi_bias(config, data, args)
        case "lri":
            plot_latency_roi_irradiance(config, data, args)
        case "lbi":
            plot_latency_bias_irradiance(config, data, args)
        case "lib":
            plot_latency_irradiance_bias(config, data, args)
        case "crb":
            plot_count_roi_bias(config, data, args)
        case "cri":
            plot_count_roi_irradiance(config, data, args)
        case "cbi":
            plot_count_bias_irradiance(config, data, args)
        case "cib":
            plot_count_irradiance_bias(config, data, args)
        case "lmap":
            plot_map(config, data, "latency", args)
        case "cmap":
            plot_map(config, data, "count", args)
        case "maproi":
            plot_map_roi(config, data, args)
        case "std":
            plot_stddev_bias_irr(config, data, args)
        case "median":
            plot_median_bias_irr(config, data, args)
        case "nbevents":
            plot_nbevents_bias_irr(config, data, args)
        case "stdroi":
            print_stddev(config, args)
        case _:
            print(HELP_MESSAGE)


def main():
    args = parse_args()

    plt.rcParams.update({'font.size': 20})
    if args.output != "":
        plt.rcParams.update({'font.size': 13})

    print("DEBUG: OUTPUT_FILE=", args.output)

    config = Config(args.latency_directory)
    data = collect_latency_data(config)

    select_mode(config, data, args)


if __name__ == "__main__":
    main()
