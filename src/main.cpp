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

#include "config.h"
#include "event_analyzer.h"
#include "latency.h"
#include "macros.h"
#include "trigger_analyzer.h"
#include <log.h/log.h>
#include <metavision/hal/facilities/i_camera_synchronization.h>
#include <metavision/hal/facilities/i_trigger_in.h>
#include <metavision/sdk/base/events/event_cd.h>
#include <metavision/sdk/driver/camera.h>
#include <metavision/sdk/ui/utils/event_loop.h>

Metavision::Camera create_camera() {
    return Metavision::Camera::from_first_available();
}

void init_camera(Metavision::Camera &cam, EventAnalyzer &event_analyzer,
                 TriggerAnalyzer &trigger_analyzer, Config &config) {
    // biases
    auto facility = cam.biases().get_facility();
    facility->set("bias_diff", config.bias_diff);
    facility->set("bias_diff_off", config.bias_diff_off);
    facility->set("bias_diff_on", config.bias_diff_on);
    facility->set("bias_fo", config.bias_fo);
    facility->set("bias_hpf", config.bias_hpf);
    facility->set("bias_refr", config.bias_refr);

    DBG(config.bias_diff);
    DBG(config.bias_diff_off);
    DBG(config.bias_diff_on);
    DBG(config.bias_fo);
    DBG(config.bias_hpf);
    DBG(config.bias_refr);

    cam.get_device().get_facility<Metavision::I_TriggerIn>()->enable(
        Metavision::I_TriggerIn::Channel::Main);
    if (config.slave) {
        WARN("sync in enabled");
        cam.get_device()
            .get_facility<Metavision::I_CameraSynchronization>()
            ->set_mode_slave();
    }

    if (config.window.width > 0 && config.window.height > 0) {
        cam.roi().set(config.window);
    } else {
        config.window.width = cam.geometry().width();
        config.window.height = cam.geometry().height();
        WARN("No roi size provided, default to full fov.");
        DBG(config.window.width);
        DBG(config.window.height);
        event_analyzer.window(config.window);
    }

    cam.cd().add_callback(PROCESS_EVENTS(event_analyzer));
    cam.ext_trigger().add_callback(PROCESS_TRIGGER(trigger_analyzer));
}

void run_camera(Metavision::Camera &cam, EventAnalyzer &event_analyzer) {

    cam.start();
    INFO("start streaming...");
    while (cam.is_running()) {
        static constexpr std::int64_t kSleepPeriodMs = 20;
        Metavision::EventLoop::poll_and_dispatch(kSleepPeriodMs);
        if (event_analyzer.should_close())
            break;
    }
    cam.stop();
    INFO("stop streaming...");
}

void dump(Config const &config, EventAnalyzer const &event_analyzer,
          TriggerAnalyzer const &trigger_analyzer) {
    INFO("dumping data...");
    LatencyInfos infos = get_latency_infos(event_analyzer, trigger_analyzer);
    std::string output_directory = config.output_directory;

    if (config.dump_latency) {
        dump_latency(infos, output_directory + "/latency.txt");
    }
    if (config.dump_map) {
        dump_latency_maps(infos, output_directory + "/map.txt");
        dump_count_maps(infos, output_directory + "/count_map.txt");
    }
    if (config.dump_counts) {
        event_analyzer.dump_events_counts(output_directory + "/counts.txt");
    }
    if (config.dump_positions) {
        event_analyzer.dump_events_positions(output_directory + "/positions.txt");
    }
    if (config.dump_triggers) {
        trigger_analyzer.dump_triggers(output_directory + "/triggers.txt");
    }
}

int main(int argc, char *argv[]) {
    Config config(argc, argv);
    Metavision::Camera cam = create_camera();
    EventAnalyzer event_analyzer(config.record_time, config.window);
    TriggerAnalyzer trigger_analyzer;

    init_camera(cam, event_analyzer, trigger_analyzer, config);
    run_camera(cam, event_analyzer);
    dump(config, event_analyzer, trigger_analyzer);
    return 0;
}
