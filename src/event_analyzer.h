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

#ifndef EVENT_ANALYZER_H
#define EVENT_ANALYZER_H
#include <fstream>
#include <log.h/log.h>
#include <map>
#include <metavision/sdk/base/events/event_cd.h>
#include <metavision/sdk/base/events/event_ext_trigger.h>
#include <metavision/sdk/base/utils/timestamp.h>
#include <metavision/sdk/driver/roi.h>

// this class will be used to analyze the events
class EventAnalyzer {
    using Event = Metavision::EventCD;

  public:
    EventAnalyzer(int64_t record_time, Metavision::Roi::Window window)
        : record_time_(record_time), window_(window) {}

  public:
    void process_events(Event const *begin, Event const *end) {
        static std::vector<Point> points0 = {};
        static std::vector<Point> points1 = {};
        auto it = begin;

        while (it != end && curr_timestamp_ < record_time_) {
            while (it != end && it->t == curr_timestamp_) {
                if (it->p == 0) {
                    points0.emplace_back(it->x, it->y);
                } else {
                    points1.emplace_back(it->x, it->y);
                }
                it++;
            }
            if (it != end) {
                events_.insert({curr_timestamp_, {points0, points1}});
                ++curr_timestamp_;
                points0 = {};
                points1 = {};
            }
        }

        if (curr_timestamp_ >= record_time_) {
            should_close_ = true;
        }
    }

  public:
    bool should_close() const { return should_close_; }

    /**
     * @brief  Dump the number of events per timestamp:
     *         timestamp count0 count1
     *         ...
     *
     * @param  filename  Output file.
     */
    void dump_events_counts(std::string const &filename) const {
        std::ofstream fs(filename);

        for (auto entry : events_) {
            fs << entry.first << " " << entry.second.points0.size() << " "
               << entry.second.points1.size() << std::endl;
        }
    }

    /**
     * @brief  Dump the coordinates of the events per timestamp
     *         timestamp
     *         count0
     *         x0 y0
     *         ...
     *         count1
     *         x1 y1
     *         ...
     *
     * @param  filename  Output file.
     */
    void dump_events_positions(std::string const &filename) const {
        std::ofstream fs(filename);
        auto dump_points = [&](std::vector<Point> const &points) {
            fs << points.size() << std::endl;
            for (auto p : points) {
                fs << (p.x - window_.x) << " " << (p.y - window_.y)
                   << std::endl;
            }
        };

        for (auto entry : events_) {
            fs << entry.first << std::endl;
            dump_points(entry.second.points0);
            dump_points(entry.second.points1);
        }
    }

  public:
    struct Point {
        uint16_t x;
        uint16_t y;
    };

    struct Events {
        std::vector<Point> points0 = {};
        std::vector<Point> points1 = {};
    };

  public:
    std::map<Metavision::timestamp, Events> const &events() const {
        return events_;
    }

    size_t record_time() const { return record_time_; }
    Metavision::Roi::Window window() const { return window_; }
    Metavision::timestamp max_timestamp() const { return curr_timestamp_; }

    size_t point_1d(Point point) const {
        size_t px = point.x - window_.x;
        size_t py = point.y - window_.y;
        return px + py * window_.width;
    }

  private:
    int64_t record_time_ = 10'000; // record time in us
    Metavision::Roi::Window window_;

    std::map<Metavision::timestamp, Events> events_ = {};
    Metavision::timestamp curr_timestamp_ = 0;
    bool should_close_ = false;
};

#endif
