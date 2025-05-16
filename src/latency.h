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

#ifndef LATENCY_H
#define LATENCY_H
#include "trigger_analyzer.h"
#include <cstddef>
#include <cstdint>
#include <map>
#include <metavision/sdk/driver/roi.h>
#include <string>
#include <vector>

using delay_t = int64_t;
using delays_t = std::vector<delay_t>;
using counts_t = std::vector<std::pair<size_t, size_t>>;

struct LatencyInfo {
    double mean = 0;
    double stddev = 0;
    double min = 0;
    double max = 0;
    double median = 0;
    size_t p0_count;
    size_t p1_count;
    delays_t latency_map;
    counts_t count_map;
};

struct LatencyInfos {
    Metavision::Roi::Window roi;
    std::map<Trigger, LatencyInfo> stimuli;
};

class EventAnalyzer;
class TriggerAnalyzer;

LatencyInfos get_latency_infos(EventAnalyzer const &event_analyzer,
                               TriggerAnalyzer const &trigger_analyzer);
void dump_latency(LatencyInfos const &infos, std::string const &filename);
void dump_latency_maps(LatencyInfos const &infos, std::string const &filename);
void dump_count_maps(LatencyInfos const &infos, std::string const &filename);

#endif
