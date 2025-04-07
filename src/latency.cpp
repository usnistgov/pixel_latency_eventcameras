// NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the
// software in any medium, provided that you keep intact this entire notice. You may improve, modify and create
// derivative works of the software or any portion of the software, and you may copy and distribute such modifications
// or works. Modified works should carry a notice stating that you changed the software and should note the date and
// nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the
// source of the software. NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND,
// EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR
// WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE
// CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS
// THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE. You
// are solely responsible for determining the appropriateness of using and distributing the software and you assume
// all risks associated with its use, including but not limited to the risks and costs of program errors, compliance
// with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of
// operation. This software is not intended to be used in any situation where a failure could cause risk of injury or
// damage to property. The software developed by NIST employees is not subject to copyright protection within the
// United States.

#include "latency.h"
#include "event_analyzer.h"
#include "trigger_analyzer.h"
#include <algorithm>
#include <cassert>
#include <cmath>
#include <numeric>
/* #define MEASUREMENT_MODE */
#define TRIGGER_START 6
#define TRIGGER_END TRIGGER_START + 2

Latency compute_latency(std::map<size_t, uint64_t> const &delays) {
    std::vector<uint64_t> values = {};

    for (auto entry : delays) {
        values.emplace_back(entry.second);
    }

    if (values.size() == 0) {
        return {};
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
    };
}

void dump_latency(EventAnalyzer const &event_analyzer,
                  TriggerAnalyzer const &trigger_analyzer,
                  std::string const &filename) {
    std::ofstream fs(filename);
    auto events = event_analyzer.events();
    auto triggers = trigger_analyzer.triggers();
    auto insert_delay = [&](auto &delays, auto const &points, uint64_t delay) {
        for (auto point : points) {
            size_t px = point.x - event_analyzer.window().x;
            size_t py = point.y - event_analyzer.window().y;
            size_t p = px + py * event_analyzer.window().width;
            if (!delays.contains(p)) {
                delays.insert({p, delay});
            }
        }
    };

#ifdef MEASUREMENT_MODE
    assert(triggers.size() > TRIGGER_END);
    for (size_t trigger_idx = TRIGGER_START; trigger_idx < TRIGGER_END; ++trigger_idx) {
#else
    for (size_t trigger_idx = 0; trigger_idx < triggers.size(); ++trigger_idx) {
#endif
        std::map<size_t, uint64_t> delays0 = {};
        std::map<size_t, uint64_t> delays1 = {};
        auto trigger_polarity = triggers.at(trigger_idx).second;
        auto trigger_timestamp = triggers.at(trigger_idx).first;
        auto next_trigger_timestamp = (trigger_idx + 1 < triggers.size())
                                          ? triggers.at(trigger_idx + 1).first
                                          : event_analyzer.max_timestamp();
        auto event = events.find(trigger_timestamp);

        while (event != events.end() && event->first < next_trigger_timestamp) {
            auto delay = event->first - trigger_timestamp;

            insert_delay(delays0, event->second.points0, delay);
            insert_delay(delays1, event->second.points1, delay);
            event++;
        }

        auto latency = trigger_polarity == 0 ? compute_latency(delays0)
                                             : compute_latency(delays1);

        char sep = ';';
        fs << trigger_polarity << sep;
        fs << latency.mean << sep;
        fs << latency.stddev << sep;
        fs << latency.min << sep;
        fs << latency.max << sep;
        fs << latency.median << sep;
        fs << delays0.size() << sep;
        fs << delays1.size() << sep;
        fs << std::endl;
    }
}
