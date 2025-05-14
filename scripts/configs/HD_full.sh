export RECORD_TIME=5000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=1280      # ROI width
export ROI_HEIGHT=720      # ROI height
export X_ITER=1            # number of ROIs on X
export Y_ITER=1            # number of ROIs on Y
export X_START=0
export Y_START=0

# default biases values
export BIAS_DIFF=0
export BIAS_DIFF_OFF=0
export BIAS_DIFF_ON=0
export BIAS_FO=0
export BIAS_HPF=0
export BIAS_REFR=0

################################################################################
#                             bias configurations                              #
################################################################################

# bias:name=BIAS_DIFF;BIAS_DIFF_OFF;BIAS_DIFF_ON;BIAS_FO;BIAS_HPF;BIAS_REFR
# use extra `#` to comment
# /!\ no spaces allowed

#bias:zero=0;0;0;0;0;0
