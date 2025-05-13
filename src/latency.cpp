// NIST-developed software is provided by NIST as a public service. You may use,
// copy and distribute copies of the software in any medium, provided that you
// keep intact this entire notice. You may improve, modify and create derivative
// works of the software or any portion of the software, and you may copy and
// distribute such modifications or works. Modified works should carry a notice
// stating that you changed the software and should note the date and nature of
// any such change. Please explicitly acknowledge the National Institute of
// Standards and Technology as the source of the software. NIST-developed
// software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND,
// EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT
// LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR
// WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR
// ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR
// MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS
// THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY,
// OR USEFULNESS OF THE SOFTWARE. You are solely responsible for determining the
// appropriateness of using and distributing the software and you assume all
// risks associated with its use, including but not limited to the risks and
// costs of program errors, compliance with applicable laws, damage to or loss
// of data, programs or equipment, and the unavailability or interruption of
// operation. This software is not intended to be used in any situation where a
// failure could cause risk of injury or damage to property. The software
// developed by NIST employees is not subject to copyright protection within the
// United States.

#include "latency.h"
#include "event_analyzer.h"
#include "trigger_analyzer.h"
#include <algorithm>
#include <cassert>
#include <cmath>
#include <numeric>

/**
 * @brief Compute informations about the latency.
 */
LatencyInfo compute_latency(std::vector<delay_t> const &delays, size_t p0_count,
                            size_t p1_count) {
    std::vector<delay_t> values = {};

    // filter non active events
    for (auto delay : delays) {
        if (delay != -1) {
            values.emplace_back(delay);
        }
    }

    if (values.size() == 0) {
        return {0, 0, 0, 0, 0, p1_count, p1_count, delays};
    }

    double sum =
        std::accumulate(values.begin(), values.end(), 0.0, std::plus<double>());
    double mean = sum / delays.size();
    double diff_sum = std::accumulate(values.begin(), values.end(), 0.0,
                                      [mean](double acc, auto delay) {
                                          double diff = delay - mean;
                                          return acc + (diff * diff);
                                      });
    double stddev = std::sqrt(diff_sum / delays.size());

    std::sort(values.begin(), values.end());

    return {
        .mean = mean,
        .stddev = stddev,
        .min = (double)values.front(),
        .max = (double)values.back(),
        .median = (double)values[values.size() / 2],
        .p0_count = p0_count,
        .p1_count = p1_count,
        .map = delays,
    };
}

/**
 * @brief Compute latency information for all the events that have been
 * generated after each trigger.
 */
LatencyInfos get_latency_infos(EventAnalyzer const &event_analyzer,
                               TriggerAnalyzer const &trigger_analyzer) {
    LatencyInfos infos(event_analyzer.window(), {});
    size_t window_size = infos.roi.width * infos.roi.height;
    auto events = event_analyzer.events();
    auto triggers = trigger_analyzer.triggers();
    auto insert_delay = [&](auto &event_delays, auto const &points,
                            delay_t delay) {
        for (auto point : points) {
            size_t p = event_analyzer.point_1d(point);
            if (event_delays[p] == -1) {
                event_delays[p] = delay;
            }
        }
        return points.size();
    };

    for (size_t trigger_idx = 0; trigger_idx < triggers.size(); ++trigger_idx) {
        std::vector<delay_t> delays0(window_size, -1);
        std::vector<delay_t> delays1(window_size, -1);
        size_t count0 = 0, count1 = 0;
        auto trigger = triggers.at(trigger_idx);
        auto event = events.find(trigger.timestamp);
        auto next_trigger_timestamp = event_analyzer.max_timestamp();
        if (trigger_idx + 1 < triggers.size()) {
            next_trigger_timestamp = triggers.at(trigger_idx + 1).timestamp;
        }

        while (event != events.end() && event->first < next_trigger_timestamp) {
            auto delay = event->first - trigger.timestamp;
            count0 += insert_delay(delays0, event->second.points0, delay);
            count1 += insert_delay(delays1, event->second.points1, delay);
            event++;
        }
        infos.stimuli.insert(
            {trigger, (trigger.polarity == 0)
                          ? compute_latency(delays0, count0, count1)
                          : compute_latency(delays1, count0, count1)});
    }
    return infos;
}

/**
 * @brief Dump latency informations for each trigger in the following format:
 *        polarity;mean;stddev;min;max;median;nb0;nb1
 */
void dump_latency(LatencyInfos const &infos, std::string const &filename) {
    std::ofstream fs(filename);
    constexpr char sep = ';';

    for (auto &stimulus : infos.stimuli) {
        auto trigger = stimulus.first;
        auto info = stimulus.second;
        fs << trigger.polarity << sep;
        fs << info.mean << sep;
        fs << info.stddev << sep;
        fs << info.min << sep;
        fs << info.max << sep;
        fs << info.median << sep;
        fs << info.p0_count << sep;
        fs << info.p1_count << sep;
        fs << std::endl;
    }
}

/**
 * @brief Dump latency for each pixels in the following format:
 *        roi_x roi_y roi_w roi_h
 *        ...
 *        polarity delay_pixel1 delay_pixel2 ...
 *        ...
 */
void dump_latency_maps(LatencyInfos const &infos, std::string const &filename) {
    std::ofstream fs(filename);

    fs << infos.roi.x << " " << infos.roi.y << " " << infos.roi.width << " "
       << infos.roi.height << std::endl;

    for (auto stimulus : infos.stimuli) {
        fs << stimulus.first.polarity;
        for (auto delay : stimulus.second.map) {
            fs << " " << delay;
        }
        fs << std::endl;
    }
}
