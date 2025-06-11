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

"""
Module that contains data types and helper functions to parse the results from
the measurements.
"""

from pathlib import Path
import yaml
import os
import numpy as np


class Stat:
    def __init__(self, polarity = 0,
                 mean = 0,
                 stddev = 0,
                 min = 0,
                 max = 0,
                 median = 0,
                 nb0 = 0,
                 nb1 = 0):
        self.polarity = polarity
        self.mean = mean
        self.stddev = stddev
        self.min = min
        self.max = max
        self.median = median
        self.nb0 = nb0
        self.nb1 = nb1


    @classmethod
    def from_values(cls, polarity, values):
        return cls(polarity, values[0], values[1], values[2], values[3],
                   values[4], values[5], values[6])


    def get(self, varidx: int):
        match varidx:
            case 0:
                return self.mean
            case 1:
                return self.stddev
            case 2:
                return self.min
            case 3:
                return self.max
            case 4:
                return self.median
            case 5:
                return self.nb0
            case 6:
                return self.nb1
        return None


def stats_mean(stats: list[Stat]) -> Stat:
    mean_latencies = [stat.mean for stat in stats]
    nb0 = [stat.nb0 for stat in stats]
    nb1 = [stat.nb1 for stat in stats]
    return Stat(stats[0].polarity, np.mean(mean_latencies),
                np.std(mean_latencies), np.min(mean_latencies),
                np.max(mean_latencies), np.median(mean_latencies), np.mean(nb0),
                np.mean(nb1))


def parse_latency_file(latency_file: str) -> tuple[Stat, Stat]:
    stats = ([], [])

    if not Path(latency_file).exists():
        print(f"ERROR: {latency_file} does not exists.")
        return None

    with open(latency_file) as latency_file:
        for line in latency_file:
            parts = line.split(';')[:-1]
            polarity = int(parts[0])
            values = list(map(float, parts[1:]))
            if values[0] == 0 or values[1]== 0:
                continue
            stats[polarity].append(Stat.from_values(polarity, values))

    return stats_mean(stats[0]), stats_mean(stats[1])


def parse_count_file(count_file):
    stats = ([], [])

    with open(count_file) as file:
        for line in file:
            fields = line.split(";")[:-1]
            polarity = int(fields[0])
            values = list(map(lambda f: float(f.split(':')[polarity]), fields[1:]))
            stats[polarity].append(Stat(polarity, values[0], values[1], values[2],
                                        values[3], values[4]))

    return stats_mean(stats[0]), stats_mean(stats[1])
