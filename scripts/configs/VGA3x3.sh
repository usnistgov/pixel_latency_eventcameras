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

#bias:zero=299;384;222;1477;1488;1500
#bias:0.25MAX=299;167;437;1477;1488;1500
#bias:0.50MAX=299;184;453;1477;1488;1500
#bias:0.75MAX=299;200;468;1477;1488;1500
#bias:0.25MIN=299;150;421;1477;1488;1500
#bias:0.50MIN=299;133;405;1477;1488;1500
#bias:0.75MIN=299;117;390;1477;1488;1500
