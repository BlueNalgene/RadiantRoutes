#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manage the SMARTS calls
"""

# Backwards Comaptibility
from __future__ import print_function

# dunders
__author__ = "Wesley T. Honeycutt"
__copyright__ = "Copyright 2025"
__credits__ = ["Wesley T. Honeycutt"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Wesley T. Honeycutt"
__email__ = "honeycutt@ou.edu"
__status__ = "alpha"


import pandas as pd
# import numpy as np
import xarray as xr

class procSMARTS:
    """
    Manage the SMARTS calls
    """
    indf = None
    log = None
    pwd = None
    # Storage for the name listed in the df header
    dfc = {\
        "hyr":None, \
        "hmon":None, \
        "hday":None, \
        "hhr":None, \
        "hmin":None, \
        "hsec":None, \
        "hlat":None, \
        "hlon":None, \
        "hseas":None, \
        "hasl":None, \
        "hagl":None, \
        "htmp":None, \
        "hrh":None, \
    }
    # Storage for the values from the df row
    dfv = {\
        "hyr":None, \
        "hmon":None, \
        "hday":None, \
        "hhr":None, \
        "hmin":None, \
        "hsec":None, \
        "hlat":None, \
        "hlon":None, \
        "hseas":None, \
        "hasl":None, \
        "hagl":None, \
        "htmp":None, \
        "hrh":None, \
    }

    def __init__(self, indf, dfhd, pwd, log=None):
        """
        | Initializes the SMARTS processor

        Parameters
        ----------
        indf : Pandas dataframe
        """
        self.indf = indf
        self.dfc["hyr"] = dfhd["dfyear"]
        self.dfc["hmon"] = dfhd["dfmon"]
        self.dfc["hday"] = dfhd["dfday"]
        self.dfc["hhr"] = dfhd["dfhr"]
        self.dfc["hmin"] = dfhd["dfmin"]
        self.dfc["hsec"] = dfhd["dfsec"]
        self.dfc["hlat"] = dfhd["dflat"]
        self.dfc["hlon"] = dfhd["dflon"]
        self.dfc["hseas"] = dfhd["dfseason"]
        self.dfc["hasl"] = dfhd["dfasl"]
        self.dfc["hagl"] = dfhd["dfagl"]
        self.dfc["htmp"] = dfhd["dft"]
        self.dfc["hrh"] = dfhd["dfrh"]
        self.pwd = pwd
        self.log = log
        return

    def get_heads(self):
        """
        | Get the appropriate header names from the DF"

        Parameters
        ----------
        """
        headers = list(self.indf.columns.values)
        for key in self.dfc:
            matches = set(headers) & set(self.dfc[key])
            if len(matches) > 1:
                if self.log: selflog.warning(f"Using first match for {key}")
            self.dfc[key] = list(matches)[0]
        return

    def create_inps(self):
        """
        | Create the SMARTS input files.  Requires status info.

        Parameters
        ----------
        """
        self.get_heads()
        # For each row in the input dataframe
        #TODO iterrows is inefficient, but I'm lazy and don't expect big df's.
        for idx, row in self.indf.iterrows():
            idx_zstr = f"{idx:06d}"
            # Cycle through headers in the dataframe,
            for key in self.dfc:
                self.dfv[key] = row[self.dfc[key]]
            # Process season naming
            if self.dfv["hseas"] == "fall":
                #NOTE SMARTS recommends WINTER here, but fall migration tends to
                #be during the June/July.  Summer makes more sense.
                self.dfv["hseas"] = "\'SUMMER\'"
            elif self.dfv["hseas"] == "spring":
                self.dfv["hseas"] = "\'SUMMER\'"
            else:
                if self.log: self.log.error(f"Season mismatch in df row {idx}")
            # Create artificial ground level
            hgl = self.dfv["hasl"] - self.dfv["hagl"]
            # Create datestring in YYYYMMdd format
            date = str(self.dfv["hyr"]) + f"{self.dfv["hmon"]:02d}" + f"{self.dfv["hday"]:02d}"
            # try:
            #     ds = xr.open_dataset(PWD + 'aod/viirs_eps_npp_aod_0.250_deg_' + s_date + '_interpAOD550.nc', engine="netcdf4")
            # except FileNotFoundError:
            #     continue
            # s_aod = ds['AOD550'].sel(lon=s_lon, lat=s_lat, method='nearest')
            # s_aod = float(s_aod.values)
            ## Create the SMARTS FORTRAN input file here.  Refer to the input
            ## Documentation for CARD definitions
            inp = ""
            # CARD1 comnt
            inp += "\'" + idx_zstr + "_allbirds\'\n"
            # CARD2 ispr
            inp += "2\n"
            # CARD2a latit, altit, height
            inp += str(self.dfv["hlat"]) + ' ' + str(hgl/1000) + ' ' + str(self.dfv["hagl"]/1000) + '\n'
            # CARD3 iatmos
            inp += "0\n"
            # CARD3a tair, rh, season, tday
            #FIXME using an average daily temperature of 25 for all data may be problematic
            inp += str(self.dfv["htmp"]) + ' ' \
                + str(self.dfv["hrh"]) + ' ' \
                + str(self.dfv["hseas"]) + ' ' \
                + str(25) + '\n'
            # CARD4 ih2o TODO calc of precip above bird might help here
            inp += "1\n"
            # CARD5 io3
            inp += "1\n"
            # CARD6 igas
            inp += "1\n"
            # CARD7 qco2 TODO get date correlated world average
            inp += "427\n"
            # CARD7a ispctr
            inp += "1\n"
            # CARD8 aeros TODO calc of rural/urban may improve model
            inp += "\'S&F_RURAL\'\n"
            # CARD9 iturb
            inp += "5\n"
             # CARD9a tau550 NOTE assume total column below 6km, see user manual TODO FIXME
            # inp += str(s_aod) + '\n'
            inp += str(0.2) + '\n'
            # CARD10 ialbdx TODO match to land type if this matters
            inp += "-1\n"
            # CARD10a rhox TODO using arbitrary broadband here, see above
            inp += "0.25\n"
            # CARD10b itilt TODO possible from some flight data
            inp += "0\n"
            # CARD11 wlmn, wlmx, suncor, solarc
            inp += "280 4000 1.024 1367.0\n"
            # CARD12 iprt
            inp += "2\n"
            # CARD12a wpmn, wpmx, intvl
            inp += "280 4000 .5\n"
            # CARD12b iotot
            inp += "6\n"
            # CARD12c iout
            inp += "2 7 8 9 10 30\n"
            # CARD13 icirc
            inp += "0\n"
            # CARD14 iscan
            inp += "1\n"
            # CARD14a ifilt, wv1, wv2, step, fwhm
            inp += "1 310 3970 2.5 30\n"
            # CARD15 illum TODO is this relevant here like for plants?
            inp += "0\n"
            # CARD16 iuv TODO potentially relevant for UV absorption
            inp += "0\n"
            # CARD17 imass TODO better airmass might help here
            inp += "3\n"
            # CARD17a
            inp += str(self.dfv["hyr"]) + ' ' \
                + str(self.dfv["hmon"]) + ' ' \
                + str(self.dfv["hday"]) + ' ' \
                + str(self.dfv["hhr"]) + ' ' \
                + str(self.dfv["hlat"]) + ' ' \
                + str(self.dfv["hlon"]) + ' 0'

            self.write_inp(idx_zstr, inp, self.log)
        return

    def write_inp(self, idx_zstr, inp, log=None):
        """
        | Write the INP to a file in the correct directory

        Parameters
        ----------
        idx_zstr : string
            6-digit string with inp file_counter
        inp : string
            content of INP file generated from this class
        """
        with open(self.pwd + "/data/smarts_inp/" + idx_zstr + ".inp.txt", 'w') as outfile:
            outfile.write(inp)
        return
