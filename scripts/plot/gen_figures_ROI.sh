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

PLOT_LATENCY_PROGRAM=../plot/plot_latency.py
INPUT_DIR=$1
OUTPUT_DIR=${INPUT_DIR}_ROI_result

mkdir -p $OUTPUT_DIR

# Configurations for stdev per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
PARAM_POL_CONFIGS=("0" "1")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
	for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
		for param_pol in ${PARAM_POL_CONFIGS[@]}; do
         	OUTPUT_FILE="${OUTPUT_DIR}/stdev_latency_per_ROI_Pol_${param_pol}_Irr_${param_irr}_Bias_${param_bias}.png"
         	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
         	--m std \
         	--i ${param_irr} \
         	--b ${param_bias} \
         	--polarity ${param_pol}  \
         	--output  \
         	-o $OUTPUT_FILE \

         done
     done
done

# Configurations for median+min+max per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
PARAM_POL_CONFIGS=("0" "1")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
	for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
		for param_pol in ${PARAM_POL_CONFIGS[@]}; do
         	OUTPUT_FILE="${OUTPUT_DIR}/median_latency_per_ROI_Pol_${param_pol}_Irr_${param_irr}_Bias_${param_bias}.png"
         	$PLOT_LATENCY_PROGRAM $INPUT_DIR \
         	--m median \
         	--i ${param_irr} \
         	--b ${param_bias} \
         	--polarity ${param_pol}  \
         	--output  \
         	-o $OUTPUT_FILE \

         done
     done
done

# Configurations for nb of events per ROI (for each irradiance and each bias):
PARAM_IRR_CONFIGS=("0.398" "0.277" "0.166" "0.046" "0.006")
PARAM_BIAS_CONFIGS=("0.75MIN" "0.50MIN" "0.25MIN" "0" "0.25MAX" "0.50MAX" "0.75MAX")
PARAM_POL_CONFIGS=("0" "1")
for param_irr in ${PARAM_IRR_CONFIGS[@]}; do
    for param_bias in ${PARAM_BIAS_CONFIGS[@]}; do
	for param_pol in ${PARAM_POL_CONFIGS[@]}; do
      	    OUTPUT_FILE="${OUTPUT_DIR}/nbevents_latency_per_ROI_Pol_${param_pol}_Irr_${param_irr}_Bias_${param_bias}.png"
            $PLOT_LATENCY_PROGRAM $INPUT_DIR \
            --m nbevents \
            --i ${param_irr} \
            --b ${param_bias} \
            --polarity ${param_pol}  \
            --output  \
            -o $OUTPUT_FILE \

         done
     done
done

