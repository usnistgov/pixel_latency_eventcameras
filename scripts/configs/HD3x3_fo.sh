export RECORD_TIME=3000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=10        # ROI width
export ROI_HEIGHT=10       # ROI height
export X_ITER=3            # number of ROIs on X
export Y_ITER=3            # number of ROIs on Y
export X_START=400
export Y_START=400

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

#bias:0_FO=0;0;0;0;0;0
#bias:0.25MAX_FO=0;0;0;14;0;0
#bias:0.50MAX_FO=0;0;0;28;0;0
#bias:0.75MAX_FO=0;0;0;42;0;0
#bias:0.25MIN_FO=0;0;0;-9;0;0
#bias:0.50MIN_FO=0;0;0;-17;0;0
#bias:0.75MIN_FO=0;0;0;-26;0;0
