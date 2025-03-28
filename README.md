# RadiantRoutes
Calculations for solar irradiation of migratory birds in flight.

## Requirements/Prerequisites

### Important Hardware Note

The design of SMARTS is heavily reliant on repeatedly moving files in the same
location on the disk. This can cause disk failures on certain types of systems
due to high frequency re-writing of the same sector. If you intend to run a
ridiculous number of entries, you should check that you are using appropriate
hardware like an enterprise-grade HDD, an adequate SSD, or other modern
hardware. If you are running an older HDD or an SD card for some reason, you
run a greater risk of sector issues.

### SMARTS 2.9.5+

The ``SMARTS`` module contains functions for calling SMARTS: Simple Model of the
Atmospheric Radiative Transfer of Sunshine, from NREL, developed by
Dr. Christian Gueymard.

SMARTS software can be obtained from:
    https://www.nrel.gov/grid/solar-resource/smarts.html

Users will be responsible to obtain a copy of SMARTS  from NREL,
honor it’s license, and download the SMART files into their PVLib folder.

### Python Environment

This requires non-standard packages. It is best practice to create a virtual
environment to run this code. Do this in your terminal:

```
virtualenv RRvenv
source RRvenv/bin/activate
pip3 install -r requirements.txt
```

When you are done, you can exit the Python environment using ``deactivate``.

If you make any changes, please remember to create a new requirements list with
`pip freeze > requirements.txt`.
