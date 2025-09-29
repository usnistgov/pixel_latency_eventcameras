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
                 signal = 0,
                 noise = 0,
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
        self.signal = signal
        self.noise = noise
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
            self.event_rate,
            self.signal,
            self.noise,
        ])


    def print(self):
        print(f"""point[{self.polarity}]: [ irradiance = {self.irradiance:6.3f}, contrast = {self.contrast:4.2f}, latency = {self.latency:10.2f}, event_rate = {self.event_rate:6.2f}, signal = {self.signal:10.2f}, noise = {self.noise:10.2f}, bias = [ bias_diff = {self.bias_diff:3}, bias_diff_off = {self.bias_diff_off:3}, bias_diff_on = {self.bias_diff_on:3}, bias_fo = {self.bias_fo:3}, bias_hpf = {self.bias_hpf:3}, bias_refr = {self.bias_refr:3} ]]""")


###############################################################################
#                               data collection                               #
###############################################################################


def parse_result_files(output_directory):
    latency_stat0, latency_stat1 = parse.parse_latency_file(output_directory / "latency.txt")
    count_stat0, count_stat1 = parse.parse_count_file(output_directory / "count.txt")
    latencies = (latency_stat0.mean, latency_stat1.mean)
    counts = (count_stat0.mean, count_stat1.mean)
    signal = (latency_stat0.nb0, latency_stat1.nb1)
    noise = (latency_stat0.nb1, latency_stat1.nb0)
    return latencies, counts, signal, noise


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
    roi_signal = ([], [])
    roi_noise = ([], [])

    for roi_dir in roi_config:
        dir = result_dir / irr_dir / bias_dir / roi_dir
        latencies, counts, signal, noise = parse_result_files(dir)
        roi_latencies[0].append(latencies[0])
        roi_latencies[1].append(latencies[1])
        roi_counts[0].append(counts[0])
        roi_counts[1].append(counts[1])
        roi_signal[0].append(signal[0])
        roi_signal[1].append(signal[1])
        roi_noise[0].append(noise[0])
        roi_noise[1].append(noise[1])

    return roi_latencies, roi_counts, roi_signal, roi_noise


def collect_latency_data(result_dir, config, data):
    # TODO: we need one axis per bias
    for irr_dir, irr_values in get_irradiance_values(config):
        for bias_dir, biases in get_biases_values(config):
            roi_latencies, roi_counts, roi_signal, roi_noise = collect_roi_data(config, result_dir,
                                                                                irr_dir, bias_dir)
            contrast = 100
            if len(irr_values) == 2:
                contrast = irr_values[1] / irr_values[0]

            point0 = Point(0, irr_values[0], contrast,
                           np.mean(roi_latencies[0]), np.mean(roi_counts[0]),
                           np.mean(roi_signal[0]), np.mean(roi_noise[0]))
            point1 = Point(1, irr_values[0], contrast,
                           np.mean(roi_latencies[1]), np.mean(roi_counts[1]),
                           np.mean(roi_signal[1]), np.mean(roi_noise[1]))
            data.append((point0.set_biases_from_list(biases),
                         point1.set_biases_from_list(biases)))


def collect_multiple_latency_data(result_dirs, data):
    for result_dir in result_dirs:
        with open(result_dir / "config.yaml") as config_file:
            config = yaml.safe_load(config_file)
            collect_latency_data(result_dir, config, data)


###############################################################################
#                             pareto optimization                             #
###############################################################################

def latency_tail_snr_loss(point1: tuple[Point, Point], point2: tuple[Point, Point]):
    latency1 = point1[0].latency + point1[1].latency
    latency2 = point2[0].latency + point2[1].latency
    latency_diff1 = abs(point1[0].latency - point1[1].latency)
    latency_diff2 = abs(point2[0].latency - point2[1].latency)
    signal1 = point1[0].signal + point1[1].signal
    signal2 = point2[0].signal + point2[1].signal
    noise1 = point1[0].noise + point1[1].noise
    noise2 = point2[0].noise + point2[1].noise

    cnd = latency2 <= latency1 \
            and latency_diff2 <= latency_diff1 \
            and signal2 >= signal1 \
            and noise2 <= noise1
    cnd_strict = latency2 < latency1 \
            or latency_diff2 < latency_diff1 \
            or signal2 > signal1 \
            or noise2 < noise1 \

    return cnd and cnd_strict


def latency_snr_pol1_loss(point1: tuple[Point, Point], point2: tuple[Point, Point]):
    latency1 = point1[1].latency
    latency2 = point2[1].latency
    signal1 = point1[1].signal
    signal2 = point2[1].signal
    noise1 = point1[1].noise
    noise2 = point2[1].noise

    cnd = latency2 <= latency1 \
            and signal2 >= signal1 \
            and noise2 <= noise1
    cnd_strict = latency2 < latency1 \
            or signal2 > signal1 \
            or noise2 < noise1 \

    return cnd and cnd_strict


def pareto_optimization(data, is_dominated):
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

    # optimals_diff = pareto_optimization(data, latency_tail_loss)
    optimals_all = pareto_optimization(data, latency_tail_snr_loss)
    optimals_p1 = pareto_optimization(data, latency_snr_pol1_loss)

    print("latency tail snr:")
    for point in filter(lambda ps: ps[0].signal > ps[0].noise and ps[1].signal > ps[1].noise, optimals_all):
        point[0].print()
        point[1].print()
        print(f"diff = {abs(point[0].latency - point[1].latency)}")

    print("latency snr polarity 1:")
    for point in filter(lambda ps: ps[0].signal > ps[0].noise and ps[1].signal > ps[1].noise, optimals_all):
        point[0].print()
        point[1].print()
        print(f"diff = {abs(point[0].latency - point[1].latency)}")


if __name__ == "__main__":
    main()
