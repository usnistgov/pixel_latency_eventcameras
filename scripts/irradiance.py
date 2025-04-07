#!/usr/bin/env python3

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

gree_LED_wavelength = 523.48
red_LED_wavelength = 680.61

delta_green = 0.2695
delta_red = 0.3584
photodiode_surface = 5e-5

red_neutral_density_filters_values = [0.6957, 0.4166, 0.1147, 0.0152]
green_neutral_density_filters_values = [0.7236, 0.4119, 0.1200, 0.0165]


def irradiance(voltage, scale, delta):
    watts = voltage / (scale * delta)
    return watts / photodiode_surface


def volt(ir, delta, scale):
    return ir * scale * delta * photodiode_surface


def main():
    print("Irradiance computation program!")
    red_voltage = input("enter the voltage of the red LED: ")
    red_power = input("enter the coefficient of the amplifier for the red LED (if 10^x enter x): ")
    green_voltage = input("enter the voltage of the green LED: ")
    green_power = input("enter the coefficient of the amplifier for the green LED (if 10^x enter x): ")

    if red_voltage and red_power:
        irr = irradiance(float(red_voltage), 10**int(red_power), delta_red)
        print("Red led:")
        print(f"\t- without filter: {irr} W/m^2")
        for idx, value in enumerate(red_neutral_density_filters_values):
            print(f"\t- with the filter {idx} ({value} %): {irr * value} W/m^2")

    if green_voltage and green_power:
        irr = irradiance(float(green_voltage), 10**int(green_power), delta_green)
        print("Green led:")
        print(f"\t- without filter: {irr} W/m^2")
        for idx, value in enumerate(green_neutral_density_filters_values):
            print(f"\t- with the filter {idx} ({value} %): {irr * value} W/m^2")


if __name__ == '__main__':
    main()
