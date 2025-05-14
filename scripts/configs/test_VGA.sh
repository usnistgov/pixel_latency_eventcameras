export RECORD_TIME=3000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=680        # ROI width
export ROI_HEIGHT=420       # ROI height
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
# #bias:0.75MIN=299;117;390;1477;1488;1500
# #bias:0.50MIN=299;133;405;1477;1488;1500
# #bias:0.25MIN=299;150;421;1477;1488;1500
# #bias:0.25MAX=299;167;437;1477;1488;1500
# #bias:0.50MAX=299;184;453;1477;1488;1500
# #bias:0.75MAX=299;200;468;1477;1488;1500

# #bias:0.75MIN_FO=299;384;222;1307;1488;1500
# #bias:0.50MIN_FO=299;384;222;1363;1488;1500
# #bias:0.25MIN_FO=299;384;222;1420;1488;1500
# #bias:0_FO=299;384;222;1477;1488;1500
# #bias:0.25MAX_FO=299;384;222;1558;1488;1500
# #bias:0.50MAX_FO=299;384;222;1639;1488;1500
# #bias:0.75MAX_FO=299;384;222;1719;1488;1500

# #bias:0.75MIN_HPF=299;384;222;1477;1047;1500
# #bias:0.50MIN_HPF=299;384;222;1477;1194;1500
# #bias:0.25MIN_HPF=299;384;222;1477;1341;1500
# #bias:0_FO=299;384;222;1477;1488;1500
# #bias:0.25MAX_HPF=299;384;222;1477;1566;1500
# #bias:0.50MAX_HPF=299;384;222;1477;1644;1500
# #bias:0.75MAX_HPF=299;384;222;1477;1722;1500

################################################################################
#                              roi configurations                              #
################################################################################

# bias:name=X_START;Y_START;WINDOW_WIDTH;WINDOW_HEIGHT
# use extra `#` to comment
# /!\ no spaces allowed

#roi:32=210;50;32;32
#roi:64=210;50;64;64
#roi:128=210;50;128;128
#roi:256=210;50;256;256
#roi:420=210;50;420;420
