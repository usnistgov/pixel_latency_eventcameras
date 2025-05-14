export RECORD_TIME=5000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=640       # ROI width
export ROI_HEIGHT=420      # ROI height
export X_ITER=1            # number of ROIs on X
export Y_ITER=1            # number of ROIs on Y
export X_START=0
export Y_START=0

# default biases values
export BIAS_DIFF=299
export BIAS_DIFF_OFF=384
export BIAS_DIFF_ON=222
export BIAS_FO=1477
export BIAS_HPF=1488
export BIAS_REFR=1500

################################################################################
#                             bias configurations                              #
################################################################################

# bias:name=BIAS_DIFF;BIAS_DIFF_OFF;BIAS_DIFF_ON;BIAS_FO;BIAS_HPF;BIAS_REFR
# use extra `#` to comment
# /!\ no spaces allowed

#bias:zero=299;384;222;1477;1488;1500
