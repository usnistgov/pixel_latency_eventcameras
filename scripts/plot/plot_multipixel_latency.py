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


def create_image(args: object):
    if args.output != "":
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        print("DEBUG: OUTPUT=", args.output)
        plt.savefig(args.output, dpi=100)
    else:
        plt.show()


def collect_multipixel_latency_data(latency_dir: Path, args: object):
    result = dict()
    multi_pixel_latency_files = dict()

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


def plot_multipixel_latency(args: object):
    polarity = int(args.polarity)
    latency_directories = args.latency_directory.split(",")
    results = dict()

    for idx, latency_dir in enumerate(latency_directories):
        result = {}
        results[f"cam {idx}"] = collect_multipixel_latency_data(Path(latency_dir), args)

    for cam in results.keys():
        result = results[cam]
        values = [latency[polarity].mean for latency in result.values()]
        # coef = np.polyfit(list(result.keys()), values, 1)
        # poly1d = np.poly1d(coef)
        std = [latency[polarity].stddev for latency in result.values()]
        print(values)
        if args.stddev:
            plt.errorbar(result.keys(), values, std, label=cam)
        else:
            x = list(result.keys())
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
