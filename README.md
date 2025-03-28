# RadiantRoutes
Calculations for solar irradiation of migratory birds in flight.

## Requirements/Prerequisites

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
