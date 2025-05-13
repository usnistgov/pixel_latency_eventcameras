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

#ifndef CONFIG_H
#define CONFIG_H
#include "log.h/log.h"
#include <argparse/argparse.hpp>
#include <metavision/sdk/driver/camera.h>

class Config {
  public:
    Config(int argc, char **argv)
        : parser("Event Camera Latency measurement program") {
        // clang-format off
        parser.add_argument("-o", "--output").required().store_into(output_directory).help("output directory name.");
        parser.add_argument("--record-time").required().store_into(record_time).help("time to record.");

        parser.add_argument("--window-x").default_value(0).store_into(window_x).help("x coordinate of the roi.");
        parser.add_argument("--window-y").default_value(0).store_into(window_y).help("y coordinate of the roi.");
        parser.add_argument("--window-width").default_value(0).store_into(window_width).help("width of the roi.");
        parser.add_argument("--window-height").default_value(0).store_into(window_height).help("height of the roi.");

        parser.add_argument("--slave").flag().store_into(slave).help("put the camera into slave mode.");

        parser.add_argument("--bias-diff").default_value(0).store_into(bias_diff).help("bias_diff");
        parser.add_argument("--bias-diff-off").default_value(0).store_into(bias_diff_off).help("bias_diff_off");
        parser.add_argument("--bias-diff-on").default_value(0).store_into(bias_diff_on).help("bias_diff_on");
        parser.add_argument("--bias-fo").default_value(0).store_into(bias_fo).help("bias_fo");
        parser.add_argument("--bias-hpf").default_value(0).store_into(bias_hpf).help("bias_hpf");
        parser.add_argument("--bias-refr").default_value(0).store_into(bias_refr).help("bias_refr");

        parser.add_argument("--dump-latency").flag().store_into(dump_latency).help("dump latency (latency.txt).");
        parser.add_argument("--dump-map").flag().store_into(dump_map).help("dump per pixel latency (map.txt).");
        parser.add_argument("--dump-counts").flag().store_into(dump_counts).help("dump event count per timestamp (counts.txt).");
        parser.add_argument("--dump-position").flag().store_into(dump_positions).help("dump all events positions (warn: can generate a heavy file) (positions.txt).");
        parser.add_argument("--dump-triggers").flag().store_into(dump_triggers).help("dump triggers (triggers.txt)");
        // clang-format on

        parser.parse_args(argc, argv);
        init();
    }

  private:
    void init() {
        DBG(window_x);
        DBG(window_y);
        DBG(window_width);
        DBG(window_height);
        DBG(output_directory);
        window = {.x = window_x,
                  .y = window_y,
                  .width = window_width,
                  .height = window_height};
        if (!dump_latency && !dump_map && !dump_counts && !dump_positions &&
            !dump_triggers) {
            dump_latency = true; // default on dump latency
        }
    }


  public:
    size_t record_time = 0;
    int window_x = 0;
    int window_y = 0;
    int window_width = 0;
    int window_height = 0;
    bool slave = false;

    bool dump_latency = true;
    bool dump_map = false;
    bool dump_counts = false;
    bool dump_positions = false;
    bool dump_triggers = false;

    int bias_diff = 0;
    int bias_diff_off = 0;
    int bias_diff_on = 0;
    int bias_fo = 0;
    int bias_hpf = 0;
    int bias_refr = 0;

    std::string output_directory;
    Metavision::Roi::Window window;

  private:
    argparse::ArgumentParser parser;
};

#endif
