export RECORD_TIME=3000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=10        # ROI width
export ROI_HEIGHT=10       # ROI height
export X_ITER=3            # number of ROIs on X
export Y_ITER=3            # number of ROIs on Y
export X_START=625
export Y_START=345

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

#bias:0_HPF=0;0;0;0;60;0
#bias:0.25MAX_HPF=0;0;0;0;75;0
#bias:0.50MAX_HPF=0;0;0;0;90;0
#bias:0.75MAX_HPF=0;0;0;0;105;0
#bias:0.25MIN_HPF=0;0;0;0;45;0
#bias:0.50MIN_HPF=0;0;0;0;30;0
#bias:0.75MIN_HPF=0;0;0;0;15;0

