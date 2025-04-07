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


################################################################################
#                                configuration                                 #
################################################################################

LATENCY_PROGRAM=../build/event_camera_latency_program

# set the camera model right here !!!
#CAMERA_MODEL="SilkyEvCamHD"
CAMERA_MODEL="SilkyEvCamVGA"
echo "running experiment with camera model "${CAMERA_MODEL}

#RECORD_TIME=20000000 #us (exposure time adapted for roi measurement)
RECORD_TIME=5000000 #us (exposure time adapted for irradiance measurement)
WINDOW_WIDTH=10  # ROI width
WINDOW_HEIGHT=10 # ROI height
X_ITER=3    # number of ROIs on X
Y_ITER=3    # number of ROIs on Y

# Configurations that will be ran:
BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
ROI_CONFIGS=("32" "64" "128" "256" "420")

# do not change this 2 variables
declare -a IRRADIANCES=() # leave empty
OUTPUT_DIRECTORY="out"

if [ "${CAMERA_MODEL}" = "SilkyEvCamHD" ]; then
	# image dim: 1280 (H) x 720 (W)
	X_START=630 # X coordinate of the first ROI
	Y_START=350 # Y coordinate of the first ROI
	# The bias config can be changed globaly or per config in the `bias_config`function
	# this is the default setting in SilkyEvCamHD
	BIAS_DIFF=0
	BIAS_DIFF_OFF=0
	BIAS_DIFF_ON=0
	BIAS_FO=0
	BIAS_HPF=0
	BIAS_REFR=0

	# SilkyEvCam HD, IMX646
	# min --> BIAS_DIFF_OFF=-35 and BIAS_DIFF_ON=-85
	# max --> BIAS_DIFF_OFF=190 and BIAS_DIFF_ON=140

	bias_config() {
	    case "$1" in
		"0.75MIN")
		    BIAS_DIFF_OFF=-25
		    BIAS_DIFF_ON=-63
		    ;;
		"0.50MIN")
		    BIAS_DIFF_OFF=-17
		    BIAS_DIFF_ON=-42
		    ;;
		"0.25MIN")
		    BIAS_DIFF_OFF=-8
		    BIAS_DIFF_ON=-21
		    ;;
		"0")
		    BIAS_DIFF_OFF=0
		    BIAS_DIFF_ON=0
		    ;;
		"0.25MAX")
		    BIAS_DIFF_OFF=47
		    BIAS_DIFF_ON=35
		    ;;
		"0.50MAX")
		    BIAS_DIFF_OFF=95
		    BIAS_DIFF_ON=70
		    ;;
		"0.75MAX")
		    BIAS_DIFF_OFF=142
		    BIAS_DIFF_ON=105
		    ;;
	    esac
	}
	roi_config() {
	    case "$1" in
		"32") X_START=420; Y_START=170; WINDOW_WIDTH=32; WINDOW_HEIGHT=32 ;;
		"64") X_START=420; Y_START=170; WINDOW_WIDTH=64; WINDOW_HEIGHT=64 ;;
		"128") X_START=420; Y_START=170; WINDOW_WIDTH=128; WINDOW_HEIGHT=128 ;;
		"256") X_START=420; Y_START=170; WINDOW_WIDTH=256; WINDOW_HEIGHT=256 ;;
		"420") X_START=420; Y_START=170; WINDOW_WIDTH=420; WINDOW_HEIGHT=420 ;;
	    esac
	}
else
	echo "setting parameters for the camera model "${CAMERA_MODEL}
	# image dim: 640 (H) x 480 (W)
	X_START=330 # X coordinate of the first ROI
	Y_START=230 # Y coordinate of the first ROI
	# The bias config can be changed globaly or per config in the `bias_config`function
	# this is the default setting in SilkyEvCamHD
	BIAS_DIFF=299
	BIAS_DIFF_ON=384
	BIAS_DIFF_OFF=222
	BIAS_FO=1477
	BIAS_HPF=1488
	BIAS_PR=1250
	BIAS_REFR=1500

	# SilkyEvCam VGA, PPS3MVCD
	# BIAS_DIFF = 299 (default)
	# min --> BIAS_DIFF_ON=bias_diff + 75 --> 374
	# max --> BIAS_DIFF_ON=bias_diff + 200 --> 499
	# min --> BIAS_DIFF_OFF=100 --> 100
	# max --> BIAS_DIFF_OFF=bias_diff - 65 --> 234

	# min --> BIAS_DIFF_OFF=0 and BIAS_DIFF_ON=0
	# max --> BIAS_DIFF_OFF=1800 and BIAS_DIFF_ON=1800
	# [HAL][WARNING] Current bias_diff_off maximal value is 234
        # [HAL][WARNING] Current bias_diff_on minimal value is 374

	bias_config() {
	    case "$1" in
		"0.75MIN")
	            echo "BIAS_DIFF "${BIAS_DIFF}
		    echo "BIAS_DIFF_OFF "${BIAS_DIFF_OFF}
		    echo "BIAS_DIFF_ON "${BIAS_DIFF_ON}
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 16))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 117))
		    echo "0.75MIN "${BIAS_DIFF_OFF}
		    echo "0.75MIN "${BIAS_DIFF_ON}
		    ;;
		"0.50MIN")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 31))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 101))
		    echo "BIAS_DIFF "${BIAS_DIFF}
		    echo "0.75MIN "${BIAS_DIFF_OFF}
		    echo "0.75MIN "${BIAS_DIFF_ON}
		    ;;
		"0.25MIN")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 47))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 84))
		    ;;
		"0")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 63))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 67))
		    #BIAS_DIFF_ON=384
		    #BIAS_DIFF_OFF=222
		    ;;
		"0.25MAX")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 79))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 50 ))
		    ;;
		"0.50MAX")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 94))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 34))
		    ;;
		"0.75MAX")
		    BIAS_DIFF_ON=$((${BIAS_DIFF} + 75 + 109))
		    BIAS_DIFF_OFF=$((${BIAS_DIFF} - 65 - 17))
		    ;;
	    esac
	}

	roi_config() {
	    case "$1" in
		"32") X_START=210; Y_START=50; WINDOW_WIDTH=32; WINDOW_HEIGHT=32 ;;
		"64") X_START=210; Y_START=50; WINDOW_WIDTH=64; WINDOW_HEIGHT=64 ;;
		"128") X_START=210; Y_START=50; WINDOW_WIDTH=128; WINDOW_HEIGHT=128 ;;
		"256") X_START=210; Y_START=50; WINDOW_WIDTH=256; WINDOW_HEIGHT=256 ;;
		"420") X_START=210; Y_START=50; WINDOW_WIDTH=420; WINDOW_HEIGHT=420 ;;
	    esac
	}
fi



################################################################################
#                                  functions                                   #
################################################################################

create_json_config() {
    echo '{' >> $RESULT_DIRECTORY/config.json

    # bias dirs
    echo '    "bias_configs":{' >> $RESULT_DIRECTORY/config.json
    NB_ELTS=${#BIAS_CONFIGS[@]}
    for ((idx=0; idx<$NB_ELTS; idx+=1)); do
        config=${BIAS_CONFIGS[$idx]}
        bias_config $config
        SUB_DIRECTORY="bias_${BIAS_DIFF}_${BIAS_DIFF_OFF}_${BIAS_DIFF_ON}_${BIAS_FO}_${BIAS_HPF}_${BIAS_REFR}"
        if [ $idx -eq $(($NB_ELTS - 1)) ]; then
            echo "        \"$config\":\"$SUB_DIRECTORY\"" >> $RESULT_DIRECTORY/config.json
        else
            echo "        \"$config\":\"$SUB_DIRECTORY\"," >> $RESULT_DIRECTORY/config.json
        fi
    done
    echo '    },' >> $RESULT_DIRECTORY/config.json

    # roi dirs
    echo '    "roi_directories_names":[' >> $RESULT_DIRECTORY/config.json
    Y_END=$(($Y_START + $WINDOW_HEIGHT * $Y_ITER))
    X_END=$(($X_START + $WINDOW_WIDTH * $X_ITER))
    for ((y=$Y_START; y<$Y_END; y+=$WINDOW_HEIGHT)); do
        for ((x=$X_START; x<$X_END; x+=$WINDOW_WIDTH)); do
            if [ $y -eq $(($Y_END - $WINDOW_HEIGHT)) ] && [ $x -eq $(($X_END - $WINDOW_WIDTH)) ]; then
                echo "        \"${x}_${y}_${WINDOW_WIDTH}_${WINDOW_HEIGHT}\"" >> $RESULT_DIRECTORY/config.json
            else
                echo "        \"${x}_${y}_${WINDOW_WIDTH}_${WINDOW_HEIGHT}\"," >> $RESULT_DIRECTORY/config.json
            fi
        done
    done
    echo '    ],' >> $RESULT_DIRECTORY/config.json

    # irradiance dirs
    echo '    "irradiance_configs":{' >> $RESULT_DIRECTORY/config.json
    NB_ELTS=${#IRRADIANCES[@]}
    for ((idx=0; idx<$NB_ELTS; idx+=1)); do
        irr=${IRRADIANCES[$idx]}
        if [ $idx -eq $(($NB_ELTS - 1)) ]; then
            echo "        \"$irr\":\"irr_$irr\"" >> $RESULT_DIRECTORY/config.json
        else
            echo "        \"$irr\":\"irr_$irr\"," >> $RESULT_DIRECTORY/config.json
        fi
    done

    # multi pixel testing dirs
    echo '    },' >> $RESULT_DIRECTORY/config.json
    echo '    "multi_pixel_latency_files":{' >> $RESULT_DIRECTORY/config.json
    NB_ELTS=${#ROI_CONFIGS[@]}
    for ((idx=0; idx<$NB_ELTS; idx+=1)); do
        config=${ROI_CONFIGS[$idx]}
        roi_config $config
        SUB_DIRECTORY="roi_${X_START}_${Y_START}_${WINDOW_WIDTH}x${WINDOW_HEIGHT}"
        if [ $idx -eq $(($NB_ELTS - 1)) ]; then
            echo "        \"$config\":\"$SUB_DIRECTORY\"" >> $RESULT_DIRECTORY/config.json
        else
            echo "        \"$config\":\"$SUB_DIRECTORY\"," >> $RESULT_DIRECTORY/config.json
        fi
    done
    echo '    }' >> $RESULT_DIRECTORY/config.json

    echo '}' >> $RESULT_DIRECTORY/config.json
}

# measure latency0;0;0;0;0;0;0;0;


measure_latency() {
    bias_config $1

    Y_END=$(($Y_START + $WINDOW_HEIGHT * $Y_ITER))
    X_END=$(($X_START + $WINDOW_WIDTH * $X_ITER))
    SUB_DIRECTORY="bias_${BIAS_DIFF}_${BIAS_DIFF_OFF}_${BIAS_DIFF_ON}_${BIAS_FO}_${BIAS_HPF}_${BIAS_REFR}"

    echo $X_START $X_END
    echo $Y_START $Y_END
    echo $SUB_DIRECTORY

    for ((y=$Y_START; y<$Y_END; y+=$WINDOW_HEIGHT)); do
        for ((x=$X_START; x<$X_END; x+=$WINDOW_WIDTH)); do
            $LATENCY_PROGRAM -o $SUB_DIRECTORY \
                --record-time $RECORD_TIME \
                --window-x $x --window-y $y \
                --window-width $WINDOW_WIDTH \
                --window-height $WINDOW_HEIGHT \
                --bias-diff $BIAS_DIFF \
                --bias-diff-off $BIAS_DIFF_OFF \
                --bias-diff-on $BIAS_DIFF_ON \
                --bias-fo $BIAS_FO \
                --bias-hpf $BIAS_HPF \
                --bias-refr $BIAS_REFR \
                --slave
        done
    done
    cat $SUB_DIRECTORY/**/latency.txt > $SUB_DIRECTORY/latencies.txt
    mv $SUB_DIRECTORY $OUTPUT_DIRECTORY
}

# running the latency program

run_bias_measure() {
    mkdir $OUTPUT_DIRECTORY
    for config in ${BIAS_CONFIGS[@]}; do
        measure_latency $config
    done
}

interative_run_bias_measure() {
    read -p 'output directory name: ' RESULT_DIRECTORY
    mkdir $RESULT_DIRECTORY

    while read -p 'irradiance (<C-d> to stop): ' IRRADIANCE; do
        IRRADIANCES+=($IRRADIANCE)
        OUTPUT_DIRECTORY=${RESULT_DIRECTORY}/irr_${IRRADIANCE}
        run_bias_measure
    done
}

run_roi_measure() {
    #mkdir $OUTPUT_DIRECTORY
    for config in ${ROI_CONFIGS[@]}; do
        roi_config $config

        echo $X_START
        echo $Y_START
        echo $WINDOW_WIDTH
        echo $WINDOW_HEIGHT

        SUB_DIRECTORY="roi_${X_START}_${Y_START}_${WINDOW_WIDTH}x${WINDOW_HEIGHT}"

        $LATENCY_PROGRAM -o $SUB_DIRECTORY \
            --record-time $RECORD_TIME \
            --window-x $X_START --window-y $Y_START \
            --window-width $WINDOW_WIDTH \
            --window-height $WINDOW_HEIGHT \
            --bias-diff $BIAS_DIFF  \
            --bias-diff-off $BIAS_DIFF_OFF  \
            --bias-diff-on $BIAS_DIFF_ON  \
            --bias-fo $BIAS_FO  \
            --bias-hpf $BIAS_HPF  \
            --bias-refr $BIAS_REFR \
            --slave

        mv $SUB_DIRECTORY $OUTPUT_DIRECTORY
    done
}

interative_run_roi_measure() {
    read -p 'output directory name: ' OUTPUT_DIRECTORY
    mkdir -p $OUTPUT_DIRECTORY
    RESULT_DIRECTORY=$OUTPUT_DIRECTORY
    run_roi_measure
}

################################################################################
#                                    script                                    #
################################################################################

if [ $# -eq 0 ]; then
    interative_run_bias_measure
else
    case $1 in
        irr)
            echo "Running variable bias measurements"
            interative_run_bias_measure
            ;;
        roi)
            echo "Running variable roi measurements"
            interative_run_roi_measure
            ;;
        help)
            echo "./measure.sh irr: irradiance measurement."
            echo "./measure.sh roi: roi measurement"
            ;;
    esac
fi
create_json_config
