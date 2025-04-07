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
        parser.add_argument("-o", "--output").required().help("output directory name");
        parser.add_argument("--record-time").required().store_into(record_time).help("time to record");
        parser.add_argument("--window-x").required().store_into(window_x).help("x coordinate of the roi");
        parser.add_argument("--window-y").required().store_into(window_y).help("y coordinate of the roi");
        parser.add_argument("--window-width").required().store_into(window_width).help("width of the roi");
        parser.add_argument("--window-height").required().store_into(window_height).help("height of the roi");
        parser.add_argument("--slave").flag().store_into(slave).help("put the camera into slave mode");

        parser.add_argument("--bias-diff").default_value(0).store_into(bias_diff).help("bias_diff");
        parser.add_argument("--bias-diff-off").default_value(0).store_into(bias_diff_off).help("bias_diff_off");
        parser.add_argument("--bias-diff-on").default_value(0).store_into(bias_diff_on).help("bias_diff_on");
        parser.add_argument("--bias-fo").default_value(0).store_into(bias_fo).help("bias_fo");
        parser.add_argument("--bias-hpf").default_value(0).store_into(bias_hpf).help("bias_hpf");
        parser.add_argument("--bias-refr").default_value(0).store_into(bias_refr).help("bias_refr");
        // clang-format on

        parser.parse_args(argc, argv);
        init();
    }

  private:
    void init() {
        root_output_directory = parser.get<>("-o");

        DBG(window_x);
        DBG(window_y);
        DBG(window_width);
        DBG(window_height);

        window = {.x = window_x,
                  .y = window_y,
                  .width = window_width,
                  .height = window_height};
        output_directory =
            get_sub_directory_name(root_output_directory, window);
    }

    std::string get_sub_directory_name(std::string const &root_output_directory,
                                       Metavision::Roi::Window window) {
        std::ostringstream oss;

        oss << root_output_directory << "/" << window.x << "_" << window.y
            << "_" << window.width << "_" << window.height << "/";
        return oss.str();
    }

  public:
    size_t record_time;
    int window_x;
    int window_y;
    int window_width;
    int window_height;
    bool slave;
    std::string root_output_directory;

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
