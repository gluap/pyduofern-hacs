# homeassistant duofern component

This uses [pyduofern](https://github.com/gluap/pyduofern) to provide (incomplete!) duofern support.
The underlying library started off as an "only those roller shutters I own and can test" port of the
(more complete but perl-based) FHEM duofern module. As of now only some roller shutters, switch actors 
and smoke detectors have been observed working in Homeassistant.

Implementing new device types requires access to a device, therefore the original implementation
supported only roller shutters and was only tested with those accessible to me via friends
and family. 

Later others contributed support for other roller shutters and smoke detectors not yet supported by the
component, but the feature set is still far from complete. Note that especially weather station support
is lacking.

With a bit of python background and enough time at hand you should be able to add support for new
device types yourself, and I am happy to merge commit requests to that end.
