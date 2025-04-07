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
#                     script to generate multiple figures                      #
################################################################################


CAMERA_MODEL="SilkyEvCamHD"
#CAMERA_MODEL="SilkyEvCamVGA"
echo "running experiment with camera model "${CAMERA_MODEL}

PLOT_LATENCY_PROGRAM=./plot_latency.py
INPUT_DIR=/home/pnb/PeterB/event_camera_latency_program/scripts/CAM1_nolens
OUTPUT_DIR=/home/pnb/PeterB/event_camera_latency_program/scripts/figures_CAM1_nolens


mkdir -p $OUTPUT_DIR
###########################################
# Configurations for Biases
PARAM_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
for param in ${PARAM_CONFIGS[@]}; do
            OUTPUT_FILE="${OUTPUT_DIR}/latency_per_ROI_forBias_${param}.png"
            $PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode lri \
            --bias ${param} \
            --output  \
            --outFile $OUTPUT_FILE \

done
#############################################
# Configurations for ROIs
if [ "${CAMERA_MODEL}" = "SilkyEvCamHD" ]; then
PARAM_CONFIGS=("630_350_10_10" "630_360_10_10" "630_370_10_10" "640_350_10_10" "640_360_10_10" "640_370_10_10" "650_350_10_10" "650_360_10_10" "650_370_10_10")
else
PARAM_CONFIGS=("330_230_10_10" "340_230_10_10" "350_230_10_10" "330_240_10_10" "340_240_10_10" "350_240_10_10" "330_250_10_10" "340_250_10_10" "350_250_10_10")
fi
for param in ${PARAM_CONFIGS[@]}; do
OUTPUT_FILE="${OUTPUT_DIR}/latency_per_bias_forROI_${param}.png"
	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode lbi \
            --roi ${param} \
            --stddev  \
            --output  \
            --outFile $OUTPUT_FILE \

done
#################################################
OUTPUT_FILE="${OUTPUT_DIR}/avg_latency_allBias_per_irr.png"
#echo $OUTPUT_FILE \
$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode lib \
            --stddev  \
            --output  \
            --outFile $OUTPUT_FILE \


#################################################
#POLARITY_VAL="0"
#OUTPUT_FILE="${OUTPUT_DIR}/multiPixel_latency_pol_${POLARITY_VAL}.png"
#echo $OUTPUT_FILE \
#$PLOT_LATENCY_PROGRAM $INPUT_DIR \
#            --mode mul \
#            --polarity $POLARITY_VAL \
#            --output  \
#            --outFile $OUTPUT_FILE \

###########################################
: '
# Configurations for stdev per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
	for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
         	OUTPUT_FILE="${OUTPUT_DIR}/std_latency_per_ROI_Irr_${param_irr}_Bias_${param_bias}.png"
         	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
         	--m std \
         	--i ${param_irr} \
         	--b ${param_bias} \
         	--output  \
         	--outFile $OUTPUT_FILE \

         done

done

# Configurations for stdev per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
	for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
         	OUTPUT_FILE="${OUTPUT_DIR}/median_latency_per_ROI_Irr_${param_irr}_Bias_${param_bias}.png"
         	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
         	--m median \
         	--i ${param_irr} \
         	--b ${param_bias} \
         	--output  \
         	--outFile $OUTPUT_FILE \

         done

done

# Configurations for stdev per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
	for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
         	OUTPUT_FILE="${OUTPUT_DIR}/nbevents_latency_per_ROI_Irr_${param_irr}_Bias_${param_bias}.png"
         	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
         	--m nbevents \
         	--i ${param_irr} \
         	--b ${param_bias} \
         	--output  \
         	--outFile $OUTPUT_FILE \

         done

done
'
###############################################
# Configurations for VMAX - applied to average latency
: '
PARAM_CONFIGS=("1000" "500" "250")
for param in ${PARAM_CONFIGS[@]}; do
	OUTPUT_FILE="${OUTPUT_DIR}/latency_map_P0_vmax_${param}.png"
	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode map \
            --width 3 \
            --height 3 \
            --vmax ${param} \
            --polarity 0 \
            --output  \
            --outFile $OUTPUT_FILE \

done

for param in ${PARAM_CONFIGS[@]}; do
	OUTPUT_FILE="${OUTPUT_DIR}/latency_map_P1_vmax_${param}.png"
	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode map \
            --width 3 \
            --height 3 \
            --vmax ${param} \
            --polarity 1 \
            --output  \
            --outFile $OUTPUT_FILE \

done
#########################
# Configurations for VMAX - applied to standard deviation of latencies
PARAM_CONFIGS=("100" "50" "25")
for param in ${PARAM_CONFIGS[@]}; do
	OUTPUT_FILE="${OUTPUT_DIR}/latency_map_P0_stdev_vmax_${param}.png"
	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode map \
            --width 3 \
            --height 3 \
            --vmax ${param} \
            --polarity 0 \
            --std  \
            --output  \
            --outFile $OUTPUT_FILE \

done

for param in ${PARAM_CONFIGS[@]}; do
	OUTPUT_FILE="${OUTPUT_DIR}/latency_map_P1_stdev_vmax_${param}.png"
	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --mode map \
            --width 3 \
            --height 3 \
            --vmax ${param} \
            --polarity 1 \
            --std  \
            --output  \
            --outFile $OUTPUT_FILE \

done
'
#read -p "Press enter to continue"

