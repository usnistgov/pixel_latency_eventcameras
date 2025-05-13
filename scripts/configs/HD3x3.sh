export RECORD_TIME=3000000 #us (exposure time adapted for irradiance measurement)
export ROI_WIDTH=10        # ROI width
export ROI_HEIGHT=10       # ROI height
export X_ITER=3            # number of ROIs on X
export Y_ITER=3            # number of ROIs on Y
export X_START=0
export Y_START=0

# default biases values
export BIAS_DIFF=0
export BIAS_DIFF_OFF=0
export BIAS_DIFF_ON=0
export BIAS_FO=0
export BIAS_HPF=0
export BIAS_REFR=0

# bias configurations
# bias:name=BIAS_DIFF;BIAS_DIFF_OFF;BIAS_DIFF_ON;BIAS_FO;BIAS_HPF;BIAS_REFR
# use extra `#` to comment
# /!\ no spaces allowed
#
#bias:0.75MIN=0;-25;-63;0;0;0
#bias:0.50MIN=0;-17;-42;0;0;0
#bias:0.25MIN=0;-8;-21;0;0;0
#bias:0=0;0;0;0;0;0
#bias:0.25MAX=0;47;35;0;0;0
#bias:0.50MAX=0;95;70;0;0;0
#bias:0.75MAX=0;142;105;0;0;0
##bias:0.75MIN_FO=0;0;0;-26;0;0
##bias:0.50MIN_FO=0;0;0;-17;0;0
##bias:0.25MIN_FO=0;0;0;-9;0;0
##bias:0_FO=0;0;0;0;0;0
##bias:0.25MAX_FO=0;0;0;14;0;0
##bias:0.50MAX_FO=0;0;0;28;0;0
##bias:0.75MAX_FO=0;0;0;42;0;0
##bias:0.75MIN_HPF=0;0;0;0;15;0
##bias:0.50MIN_HPF=0;0;0;0;30;0
##bias:0.25MIN_HPF=0;0;0;0;45;0
##bias:0_HPF=0;0;0;0;60;0
##bias:0.25MAX_HPF=0;0;0;0;75;0
##bias:0.50MAX_HPF=0;0;0;0;90;0
##bias:0.75MAX_HPF=0;0;0;0;105;0

# roi configurations
# bias:name=X_START;Y_START;WINDOW_WIDTH;WINDOW_HEIGHT
# use extra `#` to comment
# /!\ no spaces allowed
#
#roi:32=420;170;32;32
#roi:64=420;170;64;64
#roi:128=420;170;128;128
#roi:256=420;170;256;256
#roi:420=420;170;420;420
