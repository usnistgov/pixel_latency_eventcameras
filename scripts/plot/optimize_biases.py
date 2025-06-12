#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import yaml
import os
from scipy.optimize import curve_fit
import parse
import sys


class Point:
    def __init__(self,
                 polarity = 0,
                 irradiance = 0,
                 contrast = 0,
                 latency = 0,
                 event_rate = 0,
                 bias_diff = 0,
                 bias_diff_off = 0,
                 bias_diff_on = 0,
                 bias_fo = 0,
                 bias_hpf = 0,
                 bias_refr = 0):
        self.polarity = polarity
        self.irradiance = irradiance
        self.contrast = contrast
        self.latency = latency
        self.event_rate = event_rate
        self.bias_diff = bias_diff
        self.bias_diff_off = bias_diff_off
        self.bias_diff_on = bias_diff_on
        self.bias_fo = bias_fo
        self.bias_hpf = bias_hpf
        self.bias_refr = bias_refr


    def set_biases_from_list(self, biases):
        self.bias_diff = biases[0]
        self.bias_diff_off = biases[1]
        self.bias_diff_on = biases[2]
        self.bias_fo = biases[3]
        self.bias_hpf = biases[4]
        self.bias_refr = biases[5]
        return self


    def vec(self):
        return np.array([
            self.polarity,
            self.irradiance,
            self.bias_diff,
            self.bias_diff_off,
            self.bias_diff_on,
            self.bias_fo,
            self.bias_hpf,
            self.bias_refr,
            self.contrast,
            self.latency,
            self.event_rate
        ])


    def print(self):
        print(f"""
              point:
                   polarity = {self.polarity}
                   irradiance = {self.irradiance}
                   contrast = {self.contrast}
                   latency = {self.latency}
                   event_rate = {self.event_rate}
                   bias_diff = {self.bias_diff}
                   bias_diff_off = {self.bias_diff_off}
                   bias_diff_on = {self.bias_diff_on}
                   bias_fo = {self.bias_fo}
                   bias_hpf = {self.bias_hpf}
                   bias_refr = {self.bias_refr}
              """)


###############################################################################
#                               data collection                               #
###############################################################################


def parse_result_files(output_directory):
    latency_stat0, latency_stat1 = parse.parse_latency_file(output_directory / "latency.txt")
    count_stat0, count_stat1 = parse.parse_count_file(output_directory / "count.txt")
    latencies = (latency_stat0.mean, latency_stat1.mean)
    counts = (count_stat0.mean, count_stat1.mean)
    return latencies, counts


def get_irradiance_values(config):
    irradiances_config = config["irradiance_configs"]
    for irr in irradiances_config:
        irr_dir = Path(irradiances_config[irr])
        irr_values = list(map(float, irr.split(":")))
        yield irr_dir, irr_values


def get_biases_values(config):
    biases_config = config["bias_configs"]
    for bias in biases_config:
        bias_dir = biases_config[bias]
        biases = list(map(int, bias_dir.split("_")[1:]))
        yield bias_dir, biases


def collect_roi_data(config, result_dir, irr_dir, bias_dir):
    roi_config = config["roi_directories_names"]
    roi_latencies = ([], [])
    roi_counts = ([], [])

    for roi_dir in roi_config:
        dir = result_dir / irr_dir / bias_dir / roi_dir
        latencies, counts = parse_result_files(dir)
        roi_latencies[0].append(latencies[0])
        roi_latencies[1].append(latencies[1])
        roi_counts[0].append(counts[0])
        roi_counts[1].append(counts[1])

    return roi_latencies, roi_counts


def collect_latency_data(result_dir, config, data):
    # TODO: we need one axis per bias
    for irr_dir, irr_values in get_irradiance_values(config):
        for bias_dir, biases in get_biases_values(config):
            roi_latencies, roi_counts = collect_roi_data(config, result_dir,
                                                         irr_dir, bias_dir)
            contrast = 100
            if len(irr_values) == 2:
                contrast = irr_values[1] / irr_values[0]

            point0 = Point(0, irr_values[0], contrast,
                           np.mean(roi_latencies[0]), np.mean(roi_counts[0]))
            point1 = Point(1, irr_values[0], contrast,
                           np.mean(roi_latencies[1]), np.mean(roi_counts[1]))
            data.append(point0.set_biases_from_list(biases))
            data.append(point1.set_biases_from_list(biases))


def collect_multiple_latency_data(result_dirs, data):
    for result_dir in result_dirs:
        with open(result_dir / "config.yaml") as config_file:
            config = yaml.safe_load(config_file)
            collect_latency_data(result_dir, config, data)


###############################################################################
#                             pareto optimization                             #
###############################################################################


def is_dominated(point1, point2):
    return point2.latency <= point1.latency and \
           point2.event_rate <= point1.event_rate and \
           (point2.latency < point1.latency or \
            point2.event_rate < point1.event_rate)


def pareto_optimization(data):
    """
    The pareto optimization is method for solving optimization problems with a
    multi-objective function. It can be used as a stochastic method, however,
    here we do not generate any data, but we only use result of the
    measurements.
    """
    pareto_front = []

    for i, point in enumerate(data):
        is_pareto_optimal = True

        for j, other_point in enumerate(data):
            if i != j and is_dominated(point, other_point):
                is_pareto_optimal = False
                break

        if is_pareto_optimal:
            pareto_front.append(point)

    return pareto_front


###############################################################################
#                                    main                                     #
###############################################################################


def main():
    data = []
    result_dirs = []

    for arg in sys.argv[1:]:
        result_dirs.append(Path(arg))

    collect_multiple_latency_data(result_dirs, data)

    optimals0 = pareto_optimization(list(filter(lambda p: p.polarity == 0, data)))
    optimals1 = pareto_optimization(list(filter(lambda p: p.polarity == 1, data)))

    print("optimal configurations for the polarity 0:")
    for point in optimals0:
        point.print()

    print("optimal configurations for the polarity 1:")
    for point in optimals1:
        point.print()


if __name__ == "__main__":
    main()
