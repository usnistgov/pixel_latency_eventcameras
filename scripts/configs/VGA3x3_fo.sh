export RECORD_TIME=3000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=10        # ROI width
export ROI_HEIGHT=10       # ROI height
export X_ITER=3            # number of ROIs on X
export Y_ITER=3            # number of ROIs on Y
export X_START=330
export Y_START=230

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

#bias:0_FO=299;384;222;1477;1488;1500
#bias:0.25MAX_FO=299;384;222;1558;1488;1500
#bias:0.50MAX_FO=299;384;222;1639;1488;1500
#bias:0.75MAX_FO=299;384;222;1719;1488;1500
#bias:0.25MIN_FO=299;384;222;1420;1488;1500
#bias:0.50MIN_FO=299;384;222;1363;1488;1500
#bias:0.75MIN_FO=299;384;222;1307;1488;1500
