# homeassistant duofern component

This uses [pyduofern](https://github.com/gluap/pyduofern) to provide (incomplete!) duofern support.
The underlying library started off as an "only roller shutter" port of the (more complete but perl-based) FHEM
duofern module. As of now only roller shutters, switch actors and smoke detectors have been observed
working in Homeassistant.

Implementing new device types requires access to a model, therefore the original implementation
supported only shutters and . With a bit of python background and enough time at hand you
should be able to add support for new device types yourself though.

