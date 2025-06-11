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
 * @brief Compute the mean, standard deviation, median, min and max of a range
 * of values.
 */
template <template <typename> class Container, typename T>
Stats compute_stats(Container<T> &values) {
    if (values.empty()) {
        return {0};
    }
    double sum =
        std::accumulate(values.begin(), values.end(), 0.0, std::plus<T>());
    double mean = sum / (double)values.size();
    double diff_sum = std::accumulate(values.begin(), values.end(), 0.0,
                                      [mean](double acc, auto value) {
                                          double diff = value - mean;
                                          return acc + diff * diff;
                                      });
    double stddev = std::sqrt(diff_sum / values.size());
    std::sort(values.begin(), values.end());
    return {mean, stddev, (double)values.front(), (double)values.back(),
            (double)values[values.size() / 2]};
}

/**
 * @brief Create latency infos from delays and event counts.
 */
MeasurementInfo compute_latency(delays_t const &delays, counts_t const &counts,
                                size_t p0_count, size_t p1_count) {
    std::vector<delay_t> delay_values;
    std::vector<size_t> count0_values(counts.size());
    std::vector<size_t> count1_values(counts.size());

    for (size_t i = 0; i < delays.size(); ++i) {
        if (delays[i] > 0) {
            delay_values.push_back(delays[i]);
        }
        count0_values[i] = counts[i].nb0;
        count1_values[i] = counts[i].nb1;
    }

    auto latency_stats = compute_stats(delay_values);
    auto count0_stats = compute_stats(count0_values);
    auto count1_stats = compute_stats(count1_values);

    MeasurementInfo result{
        .latency_stats = latency_stats,
        .count0_stats = count0_stats,
        .count1_stats = count1_stats,
        .total_count = {p0_count, p1_count},
        .latency_map = delays,
        .count_map = counts,
    };
    return result;
}

size_t insert_infos(EventAnalyzer const &event_analyzer, int16_t polarity,
                    auto &event_delays, auto &event_counts, auto const &points,
                    delay_t delay) {
    for (auto point : points) {
        size_t p = event_analyzer.point_1d(point);
        if (event_delays[p] == -1) {
            event_delays[p] = delay;
        }
        if (polarity == 0) {
            event_counts[p].nb0++;
        } else {
            event_counts[p].nb1++;
        }
    }
    return points.size();
}

/**
 * @brief Compute latency information for all the events that have been
 *        generated after each trigger.
 */
MeasurementInfos
get_measurement_infos(EventAnalyzer const &event_analyzer,
                      TriggerAnalyzer const &trigger_analyzer) {
    MeasurementInfos infos(event_analyzer.window(), {});
    // the ROI size is wrong on the camera...
    size_t window_size = (infos.roi.width + 1) * (infos.roi.height + 1);
    auto events = event_analyzer.events();
    auto triggers = trigger_analyzer.triggers();
    delays_t delays0(window_size);
    delays_t delays1(window_size);
    counts_t counts(window_size);

    for (size_t trigger_idx = 0; trigger_idx < triggers.size(); ++trigger_idx) {
        size_t nb_off_events = 0, nb_on_events = 0;
        auto trigger = triggers.at(trigger_idx);
        auto event = events.find(trigger.timestamp);

        // get end timestamp
        auto next_trigger_timestamp = event_analyzer.max_timestamp();
        if (trigger_idx + 1 < triggers.size()) {
            next_trigger_timestamp = triggers.at(trigger_idx + 1).timestamp;
        }

        // reset data arrays
        std::fill(delays0.begin(), delays0.end(), -1);
        std::fill(delays1.begin(), delays1.end(), -1);
        std::fill(counts.begin(), counts.end(), EventCount{0, 0});

        while (event != events.end() && event->first < next_trigger_timestamp) {
            auto delay = event->first - trigger.timestamp;
            nb_off_events += insert_infos(event_analyzer, 0, delays0, counts,
                                          event->second.points0, delay);
            nb_on_events += insert_infos(event_analyzer, 1, delays1, counts,
                                         event->second.points1, delay);
            event++;
        }
        if (nb_on_events == 0 && nb_off_events == 0) {
            WARN("no events");
            continue;
        }
        infos.stimuli.insert(
            {trigger,
             (trigger.polarity == 0)
                 ? compute_latency(delays0, counts, nb_off_events, nb_on_events)
                 : compute_latency(delays1, counts, nb_off_events,
                                   nb_on_events)});
    }
    return infos;
}

/**
 * @brief Dump latency stats for each trigger in the following format:
 *        polarity;mean;stddev;min;max;median;nb0;nb1
 */
void dump_latency_stats(MeasurementInfos const &infos,
                        std::string const &filename) {
    std::ofstream fs(filename);
    constexpr char sep = ';';

    for (auto &stimulus : infos.stimuli) {
        auto trigger = stimulus.first;
        auto info = stimulus.second;
        fs << trigger.polarity << sep;
        fs << info.latency_stats.mean << sep;
        fs << info.latency_stats.stddev << sep;
        fs << info.latency_stats.min << sep;
        fs << info.latency_stats.max << sep;
        fs << info.latency_stats.median << sep;
        fs << info.total_count.nb0 << sep;
        fs << info.total_count.nb1 << sep;
        fs << std::endl;
    }
}

/**
 * @brief Dump event rate stats for each trigger in the following format:
 *        polarity;mean0:1;stddev0:1;min0:1;max0:1;median0:1
 */
void dump_count_stats(MeasurementInfos const &infos,
                      std::string const &filename) {
    std::ofstream fs(filename);
    constexpr char sep = ';';
    constexpr char count_stat_sep = ':';

    for (auto &stimulus : infos.stimuli) {
        auto trigger = stimulus.first;
        auto info = stimulus.second;
        fs << trigger.polarity << sep;
        fs << info.count0_stats.mean << count_stat_sep << info.count1_stats.mean
           << sep;
        fs << info.count0_stats.stddev << count_stat_sep
           << info.count1_stats.stddev << sep;
        fs << info.count0_stats.min << count_stat_sep << info.count1_stats.min
           << sep;
        fs << info.count0_stats.max << count_stat_sep << info.count1_stats.max
           << sep;
        fs << info.count0_stats.median << count_stat_sep
           << info.count1_stats.median << sep;
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
void dump_latency_maps(MeasurementInfos const &infos,
                       std::string const &filename) {
    std::ofstream fs(filename);

    fs << infos.roi.x << " " << infos.roi.y << " " << infos.roi.width << " "
       << infos.roi.height << std::endl;

    for (auto stimulus : infos.stimuli) {
        fs << stimulus.first.polarity;
        for (auto delay : stimulus.second.latency_map) {
            fs << " " << delay;
        }
        fs << std::endl;
    }
}

/**
 * @brief Dump activation count for each pixels in the following format:
 *        roi_x roi_y roi_w roi_h
 *        ...
 *        polarity nv_off:nb_on ...
 *        ...
 */
void dump_count_maps(MeasurementInfos const &infos,
                     std::string const &filename) {
    std::ofstream fs(filename);

    fs << infos.roi.x << " " << infos.roi.y << " " << infos.roi.width << " "
       << infos.roi.height << std::endl;

    for (auto stimulus : infos.stimuli) {
        fs << stimulus.first.polarity;
        for (auto count : stimulus.second.count_map) {
            fs << " " << count.nb0 << ":" << count.nb1;
        }
        fs << std::endl;
    }
}
