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
from parse import Stat, parse_latency_file

# ../../plot/plot_multipixel_latency.py CAM1_nolens_roi,CAM2_nolens_roi,CAM3_nolens_roi2 --stddev --logY --polarity=1 -o out.png

def create_image(args: object):
    if args.output != "":
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(16, 6)
        print("DEBUG: OUTPUT=", args.output)
        plt.savefig(args.output, dpi=100)
    else:
        plt.show()


def collect_multipixel_latency_data(latency_dir: Path, args: object):
    result = dict()
    multi_pixel_latency_files = dict()

    print(f"parse {latency_dir}/config.yaml")

    with open(Path(latency_dir) / "config.yaml") as config_file:
        config = yaml.safe_load(config_file)
        multi_pixel_latency_files = config["multi_pixel_latency_files"]

    for size in multi_pixel_latency_files:
        dir = Path(multi_pixel_latency_files[size])
        latency_file = latency_dir / dir / "latency.txt"
        print("DEBUG: latency_dir=", latency_dir, ", dir=", dir, ", latency_file=", latency_file)
        stats = parse_latency_file(latency_file)
        if stats == None:
            continue
        result[int(size)] = stats

    return result


def plot_multipixel_latency(args: object):
    polarity = int(args.polarity)
    latency_directories = args.latency_directory.split(",")
    results = dict()
    fig, (ax0, ax1) = plt.subplots(1, 2)

    for idx, latency_dir in enumerate(latency_directories):
        result = {}
        results[f"cam {idx}"] = collect_multipixel_latency_data(Path(latency_dir), args)

    for cam in results.keys():
        result = results[cam]
        values0 = [latency[0].mean for latency in result.values()]
        values1 = [latency[1].mean for latency in result.values()]
        # coef = np.polyfit(list(result.keys()), values, 1)
        # poly1d = np.poly1d(coef)
        std0 = [latency[0].stddev for latency in result.values()]
        std1 = [latency[1].stddev for latency in result.values()]
        if args.stddev:
            ax0.errorbar(result.keys(), values0, std0, label=cam)
            ax1.errorbar(result.keys(), values1, std1, label=cam)
        else:
            x = list(result.keys())
            ax0.plot(x, values0, label=cam)
            ax1.plot(x, values1, label=cam)

    ax0.set_ylabel("latency (us)")
    ax0.set_xlabel("nb pixels")
    ax1.set_xlabel("nb pixels")
    ax0.set_title("polarity 0")
    ax1.set_title("polarity 1")
    fig.suptitle("Latency over ROI sizes")
    if args.logX:
        ax0.set_xscale("log")
        ax1.set_xscale("log")
    if args.logY:
        ax0.set_yscale("log")
        ax1.set_yscale("log")
    ax0.legend()
    ax1.legend()
    ylim0 = ax0.get_ylim()
    ylim1 = ax1.get_ylim()
    ylim = (min(ylim0[0], ylim1[0]), max(ylim0[1], ylim1[1]))
    ax0.set_ylim(ylim)
    ax1.set_ylim(ylim)
    create_image(args)


def parse_args():
    parser = argparse.ArgumentParser("plot_latency")
    parser.add_argument("latency_directory")
    parser.add_argument("-std",
                        "--stddev",
                        action="store_true",
                        help="plot the standard deviation using errorbars")
    parser.add_argument("-logX", "--logX", action="store_true",
                        help="use log scale")
    parser.add_argument("-logY", "--logY", action="store_true",
                        help="use log scale")
    parser.add_argument("-P", "--polarity", default=1)
    parser.add_argument("-o", "--output", default="", required=False)
    return parser.parse_args()


def main():
    args = parse_args()
    plot_multipixel_latency(args)


if __name__ == "__main__":
    main()
