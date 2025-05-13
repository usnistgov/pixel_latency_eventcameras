#!/usr/bin/env bash

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

set -euo pipefail

################################################################################
#                                configuration                                 #
################################################################################

LATENCY_PROGRAM=../../build/event_camera_latency_program
CONFIG_FILE="$1"
LOG_FILE=~/log.txt
declare -a IRRADIANCES=()
declare -a BIAS_CONFIGS=()
declare -a ROI_CONFIGS=()

parse_config() {
    source "$CONFIG_FILE"
    export Y_END=$((Y_START + ROI_HEIGHT * Y_ITER))
    export X_END=$((X_START + ROI_WIDTH * X_ITER))

    for line in $(grep "^#bias:" "$CONFIG_FILE"); do
        BIAS_CONFIGS+=($line)
    done

    for line in $(grep "^#roi:" "$CONFIG_FILE"); do
        ROI_CONFIGS+=($line)
    done
}

bias_config() {
    local vals=$(echo $1 | awk -F'=' '{ print $2 }')

    export CONFIG_NAME=$(echo $1 | awk -F'=' '{ print $1 }' | sed 's/#bias://')

    # biases values
    export BIAS_DIFF=$(echo $vals | awk -F';' '{ print $1 }')
    export BIAS_DIFF_OFF=$(echo $vals | awk -F';' '{ print $2 }')
    export BIAS_DIFF_ON=$(echo $vals | awk -F';' '{ print $3 }')
    export BIAS_FO=$(echo $vals | awk -F';' '{ print $4 }')
    export BIAS_HPF=$(echo $vals | awk -F';' '{ print $5 }')
    export BIAS_REFR=$(echo $vals | awk -F';' '{ print $6 }')
}

roi_config() {
    local vals=$(echo $1 | awk -F'=' '{ print $2 }')

    export CONFIG_NAME=$(echo $1 | awk -F'=' '{ print $1 }' | sed 's/#roi://')

    # roi values
    export X_START=$(echo $vals | awk -F';' '{ print $1 }')
    export Y_START=$(echo $vals | awk -F';' '{ print $2 }')
    export ROI_WIDTH=$(echo $vals | awk -F';' '{ print $3 }')
    export ROI_HEIGHT=$(echo $vals | awk -F';' '{ print $4 }')
}

################################################################################
#                             json file generation                             #
################################################################################

json_dump_biases() {
    echo "    \"bias_configs\":{"
    NB_ELTS=${#BIAS_CONFIGS[@]}
    for ((idx = 0; idx < NB_ELTS; idx += 1)); do
        config=${BIAS_CONFIGS[$idx]}
        bias_config "$config" >/dev/null
        sub_dir="bias_${BIAS_DIFF}_${BIAS_DIFF_OFF}_${BIAS_DIFF_ON}_${BIAS_FO}_${BIAS_HPF}_${BIAS_REFR}"
        echo -n "        \"$CONFIG_NAME\":\"$sub_dir\""
        [ $idx -eq $((NB_ELTS - 1)) ] && echo "" || echo ","
    done
    echo "    },"
}

json_dump_rois() {
    echo "    \"roi_directories_names\":["
    local x_last=$((X_END - ROI_WIDTH))
    local y_last=$((Y_END - ROI_HEIGHT))
    for ((y = Y_START; y < Y_END; y += ROI_HEIGHT)); do
        for ((x = X_START; x < X_END; x += ROI_WIDTH)); do
            echo -n "        \"${x}_${y}_${ROI_WIDTH}_${ROI_HEIGHT}\""
            [ $y -eq $y_last ] && [ $x -eq $x_last ] && echo "" || echo ","
        done
    done
    echo "    ],"
}

json_dump_irradiances() {
    echo "    \"irradiance_configs\":{"
    NB_ELTS=${#IRRADIANCES[@]}
    for ((idx = 0; idx < NB_ELTS; idx += 1)); do
        irr=${IRRADIANCES[$idx]}
        echo -n "        \"$irr\":\"irr_$irr\""
        [ $idx -eq $((NB_ELTS - 1)) ] && echo "" || echo ","
    done
    echo "    },"
}

json_dump_multipixels() {
    echo "    \"multi_pixel_latency_files\":{"
    NB_ELTS=${#ROI_CONFIGS[@]}
    for ((idx = 0; idx < NB_ELTS; idx += 1)); do
        config=${ROI_CONFIGS[$idx]}
        roi_config "$config" >/dev/null
        sub_dir="roi_${X_START}_${Y_START}_${ROI_WIDTH}x${ROI_HEIGHT}"
        echo -n "        \"$CONFIG_NAME\":\"$sub_dir\""
        [ $idx -eq $((NB_ELTS - 1)) ] && echo "" || echo ","
    done
    echo "    }"
}

create_json_config() {
    echo "{"
    json_dump_biases
    json_dump_rois
    json_dump_irradiances
    json_dump_multipixels
    echo "}"
}

################################################################################
#                              measure functions                               #
################################################################################

run_latency_program() {
    $LATENCY_PROGRAM -o "$1" \
        --record-time "$RECORD_TIME" \
        --window-x "$2" --window-y "$3" \
        --window-width "$ROI_WIDTH" \
        --window-height "$ROI_HEIGHT" \
        --bias-diff "$BIAS_DIFF" \
        --bias-diff-off "$BIAS_DIFF_OFF" \
        --bias-diff-on "$BIAS_DIFF_ON" \
        --bias-fo "$BIAS_FO" \
        --bias-hpf "$BIAS_HPF" \
        --bias-refr "$BIAS_REFR" \
        --dump-latency \
        --dump-map \
        --slave
}

measure_latency() {
    bias_config "$3"

    output_dir=$1
    irradiance_dir=$2
    bias_dir="bias_${BIAS_DIFF}_${BIAS_DIFF_OFF}_${BIAS_DIFF_ON}_${BIAS_FO}_${BIAS_HPF}_${BIAS_REFR}"
    dir="$output_dir/$irradiance_dir/$bias_dir"

    echo "measure: $dir"

    for ((y = Y_START; y < Y_END; y += ROI_HEIGHT)); do
        for ((x = X_START; x < X_END; x += ROI_WIDTH)); do
            roi_dir="$dir/${x}_${y}_${ROI_WIDTH}_${ROI_HEIGHT}"
            mkdir -p "$roi_dir"
            run_latency_program "$roi_dir" "$x" "$y"
        done
    done
}

run_bias_measure() {
    mkdir -p "$1/irr_$2"
    for config in "${BIAS_CONFIGS[@]}"; do
        if [[ "${config:0}" != "#" ]]; then
            measure_latency "$1" "irr_$2" "$config"
        fi
    done
}

interative_run_bias_measure() {
    local output_dir="out"

    read -r -p 'output directory name: ' output_dir
    mkdir -p "$output_dir"

    while read -r -p 'irradiance (<C-d> to stop): ' irr; do
        echo "JOB-INFO: start measurement for irradiance $irr." >$LOG_FILE
        echo "chosen irradiance: $irr"
        IRRADIANCES+=("$irr")
        run_bias_measure "$output_dir" "$irr"
        echo "JOB-INFO: measurement for irradiance $irr finished." >>$LOG_FILE
    done
    create_json_config >"$output_dir/config.json"
}

run_roi_measure() {
    local output_dir="$1"

    for config in "${ROI_CONFIGS[@]}"; do
        local dir="$output_dir/roi_${X_START}_${Y_START}_${ROI_WIDTH}x${ROI_HEIGHT}"

        mkdir -p "$dir"
        echo "$X_START $Y_START $ROI_WIDTH $ROI_HEIGHT"
        roi_config "$config"
        run_latency_program "$dir" "$X_START" "$Y_START"
    done
}

interative_run_roi_measure() {
    local output_dir="out"

    read -r -p 'output directory name: ' output_dir
    mkdir -p "$output_dir"
    echo "JOB-INFO: start ROI measurements." >$LOG_FILE
    run_roi_measure "$output_dir"
    create_json_config >"$output_dir/config.json"
}

################################################################################
#                                    script                                    #
################################################################################

parse_config

if [ $# -eq 1 ]; then
    echo "Running variable bias measurements"
    interative_run_bias_measure
else
    case $2 in
    irr)
        echo "Running variable bias measurements"
        interative_run_bias_measure
        ;;
    roi)
        echo "Running variable roi measurements"
        interative_run_roi_measure
        ;;
    help)
        echo "./measure.sh <config-file> irr: irradiance measurement."
        echo "./measure.sh <config-file> roi: roi measurement"
        ;;
    esac
fi

echo "JOB-DONE" >>$LOG_FILE
