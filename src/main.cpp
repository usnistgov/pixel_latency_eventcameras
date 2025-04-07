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

#include "config.h"
#include "event_analyzer.h"
#include "latency.h"
#include "macros.h"
#include "trigger_analyzer.h"
#include <filesystem>
#include <log.h/log.h>
#include <metavision/hal/facilities/i_camera_synchronization.h>
#include <metavision/hal/facilities/i_trigger_in.h>
#include <metavision/sdk/base/events/event_cd.h>
#include <metavision/sdk/driver/camera.h>
#include <metavision/sdk/ui/utils/event_loop.h>
//#define DUMP_ALL

Metavision::Camera create_camera() {
    return Metavision::Camera::from_first_available();
}

void init_camera(Metavision::Camera &cam, EventAnalyzer &event_analyzer,
                 TriggerAnalyzer &trigger_analyzer,
                 Metavision::Roi::Window window, Config const &config) {
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

    cam.roi().set(window);

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

void dump(EventAnalyzer const &event_analyzer,
          TriggerAnalyzer const &trigger_analyzer,
          std::string const &output_directory) {
    INFO("dumping data...");
    #ifdef DUMP_ALL
    event_analyzer.dump_events_counts(output_directory + "counts.txt");
    event_analyzer.dump_events_positions(output_directory + "positions.txt");
    trigger_analyzer.dump_triggers(output_directory + "triggers.txt");
    #endif
    dump_latency(event_analyzer, trigger_analyzer, output_directory + "latency.txt");
}

int main(int argc, char *argv[]) {
    Config config(argc, argv);
    Metavision::Camera cam = create_camera();
    EventAnalyzer event_analyzer(config.record_time, config.window);
    TriggerAnalyzer trigger_analyzer;

    std::filesystem::create_directory(config.root_output_directory);
    if (!std::filesystem::create_directory(config.output_directory)) {
        ERROR("cannot override existing sub directory.");
        return 1;
    }

    init_camera(cam, event_analyzer, trigger_analyzer, config.window,
                config);
    run_camera(cam, event_analyzer);
    dump(event_analyzer, trigger_analyzer, config.output_directory);
    return 0;
}
