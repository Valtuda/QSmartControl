# QSmartControl
A Python implementation of the Quantel Q-Smart laser controls.

*Note: I noticed telnetlib is deprecated. I will get around to rewriting this at some point, but until then you're welcome to fork or suggest changes.*

# What does it do?
This repo serves to provide a Python package to expose the Q-Smart laser controls through easily accessible interface, so no direct commands to the interface have to be given.

# Documentation
There is no full documentation at the moment. The package consists of two classes: 
- LaserCommunication which deals with the Telnet messages, we won't provide any info on this.
- LaserSettings which interfaces between the user and the laser.

# Settings from dictionary
Settings can be exported to a dictionary and imported as a dictionary using the to_dict() and settings_from_dict functions.

# LaserSettings
LaserSettings has the following properties. Properties marked with an asterisk are read-only. Properties marked with a double astrisk require "admin mode" to be enabled as they can change laser performance.
- cooling_temp\*: returns cooling water temperature
- powersupply_version\*: returns powersupply firmware version
- laserbrain_version\*: returns laserbrain firmware version
- state\*: returns state of the laser as a number (see manual)
- state_str\*: returns state of the laser as a string
- flashlamp_voltage\*\*: Flashlamp voltage in V
- flastlamp_pulse_width\*\*: Flashlamp pulse width in us.
- flashlamp_shots\*: Number of shots of the flashlamp, system-tracked.
- flashlamp_trigger: Flashlamp Trigger Mode (either "Internal" or "External")
- qswitch_trigger: QSwitch Trigger Mode (either "Internal" or "External")
- mode\*: Mode the laser is operating in ("Burst", "F/N Mode" or "Scan"). See also set_mode()

The class also has the following methods to further influence the laser:
- get_cooling_temp: Same as cooling_temp
- get_state: Same-ish as state/state_str
- enable_flash: Enables flashlamp
- disable_flash: Disables flashlamp
- enable_qsw: Enables Q-Switch
- disable_qsw: Disables Q-Switch
- set_both_triggers: Allows setting both flashlamp and Q-switch triggers
- set_mode: Allows setting of the "mode" parameter. Check source file for exact use.
