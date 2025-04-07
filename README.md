# Event Camera latency measurement program

This program can be used to measure the latency of the event cameras that
support OpenEB. The script are used to build graphs that presents the results.

## Requirements

- [OpenEB](https://github.com/prophesee-ai/openeb/tree/4.6.2) version `4.6.2` (usually installed through the sdk).
- Compatible event camera installation (see camera constructor instructions).
- C++ compiler that supports `C++20`.

## Project setup

Clone the repo with submodules:

```sh
git clone --recurse-submodules <url>
```

To clone the submodules **if the `--recurse-submodules` options wasn't used**:

```sh
git submodules init
git submodules update
```

If you use a custom build of OpenEB that is not in your path, you can specify
the location threw `CUSTOM_LIB_DIR` as follows:

```sh
mkdir build; cd build
cmake .. -DCUSTOM_LIB_DIR=<path/to/custom_dir/>
```

## Output files

The main program will use the camera to record events during a certain amount of
time (configurable). The `plot_latency.py` script uses the `latency.txt` files.
The proper directory structure is created by the `measure.sh` script. The
`latency.txt` files have the following format:

```
polarity;average latency;stddev;min;max;median;nb polarity 0 events;nb polarity 1 events;
```

The `plot.py` script is used to make statistics and display the positions of the
events. It requires the three files bellow, however, to generate them, the
program must be compiled with the `DUMP_ALL` preprocessor constant defined:

- `counts.txt`: gives the number of events of both polarity for each timestamp.
  This file can be used to determin the global latency for the exeperiment.
- `positions.txt`: for each timestamp, list all the events and their positions.
  This file can be used to determin the pixel latency for the experiment.
- `triggers.txt`: list of trigger events and their corresponding timestamp.

## Latency measurement

All the scripts are in the `script` directory.

### Measure script

The script `measure.sh` is used to measure the latency. It takes one option as
argument:

- `irr`: measure the latency for different irradiances.
- `roi`: measure the latency for different ROI.

```sh
./measure.sh irr
./measure.sh roi
```

The script must be configured before being used. The configuration is done by
modifying the global variables and the functions in the *configuration* section
of the script.

The script is interactive, so it will prompt for the name of the output
directory. In `roi` mode, it will also prompt for the irradiance. In this case,
change the neutral density filter and enter the new irradiance value. Press
`CTRL-d` when finished. A `config.json` will be generated automatically for the
`plot_latency.py` script. The configuration can be changed to exclude
measurements or reorder the bias configurations.

### Irradiance script

The `irradiance` script is used to compute the irradiance for the red and green
LEDs. It is an interative program that ask for the voltage and the amplifier
coefficient, and computes the irradiance for all the filters we use.

### Plot latency script

```sh
# help
./plot_latency.py -h

# display the modes documentation
./plot_latency.py output_dir -m help

# plot latency per ROI over bias the configurations for a specific irradiance
./plot_latency.py output_dir -m lrb -i 0.01

# plot latency per ROI over the irradiance for a specific bias configuration
./plot_latency.py output_dir -m lri -b zero

# plot latency per bias configurations over the irradiance for a specific ROI
./plot_latency.py output_dir -m lbi -r 630_350_10_10

# plot the average latency on all the ROIs per irradiance over bias configurations
./plot_latency.py output_dir -m lib

# plot multi pixel latency (cv roi mode)
./plot_latency.py output_dir -m mul --polarity 1

# plot latency map:
# - W is the value of X_ITER (see measure.sh)
# - H is the value of Y_ITER (see measure.sh)
# - M is the maximum latency value
# This mode is used to track problematic ROIs, in which the latency was too big.
# All the ROIs that have a latency superior or equal to the max value (M) will
# be collored in yellow.
./plot_latency.py output_dir -m map -W 3 -H 3 -M 1000

# plot the standard deviation for a particular bias and irradiance
./plot_latency.py output_dir -m std -b zero -i 0.01

# print the standard deviation between the rois
./plot_latency.py output_dir -m stdroi
```

Other options:
- `-std`: add the standard deviation to the plots.
- `-P`: specify the polarity (used with `map` and `mul`).

### Statistic plots


The results can be seen using the `scripts/plot.py` script that can be used as
follows:

```sh
# display stats
./plot.py file trigger_file --program=stat

# generate the standard plot (no process) on the given range
./plot.py file trigger_file --program=plot

# generate the average plot on the given range (period size is 50 here)
./plot.py file trigger_file --program=avg,50

# generate a plot that contains the positions of the events
./plot.py file trigger_file --program=pos,128
```

The options:

- `file`: either `counts.txt` or `positions.txt`.
- `trigger_file`: path to `triggers.txt`.
- `--program`: selection of the output. There outputs are available:
  - `stat` (**counts file**): will just display some statistics on the events
    (average, median, ...).
  - `plot` (**counts file**): will plot the number of events as well as the
    triggers.
  - `avg,N` (**counts file**): will plot the average number of events. The
    average is computed on a time windows of size `N`.
  - `pos,W` (**positions file**): plot the events per timestamp. The `y` axis is
    the position off the event in 1D, and the position is computed using the
    specified camera width `W` (`position = x + y*W`).

# Contacts

- [Peter Bajcsy](peter.bajcsy@nist.gov) (peter.bajcsy@nist.gov)
- [Timothy Blattner](timothy.blattner@nist.gov) (timothy.blattner@nist.gov)
- [Remi Chassagnol](remi.chassagnol@nist.gov) (remi.chassagnol@nist.gov)

NIST Information Technology Laboratory (ITL), Software and Systems Division
(SSD), Information Systems Group (ISG).
