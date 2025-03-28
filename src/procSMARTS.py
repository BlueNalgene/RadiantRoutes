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

from glob import glob
import os
import pandas as pd
import shutil
import subprocess
import xarray as xr


class procSMARTS:
    """
    Manage the SMARTS calls
    """
    indf = None
    runid = None
    log = None
    pwd = None
    outarray = None
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

    def __init__(self, indf, runid, dfhd, pwd, log=None):
        """
        | Initializes the SMARTS processor

        Parameters
        ----------
        indf : Pandas dataframe
        """
        self.indf = indf
        self.runid = runid
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

            self.write_inp(idx_zstr, inp)
        return

    def write_inp(self, idx_zstr, inp):
        """
        | Write the INP to a file in the correct directory

        Parameters
        ----------
        idx_zstr : string
            6-digit string with inp file_counter
        inp : string
            content of INP file generated from this class
        """
        with open(self.pwd + "/data/smarts_inp/" + self.runid + '_' + idx_zstr + ".inp.txt", 'w') as outfile:
            outfile.write(inp)
            if self.log: self.log.info(f"created {self.runid + '_' + idx_zstr}.inp.txt")
        return

    def file_path(self, path):
        """
        | Check that the os.path is actually a file.  Else raises an error.

        Parameters
        ----------
        path : string
        stringlike path to check

        Returns
        -------
        path : string
        stringlike path to file
        """
        # requires = ["os"]
        # for i in requires: check_import(i, log=log)
        if not os.path.isfile(path):
            if self.log:
                self.log.error(f"readable_file:{path} is not a valid to a file")
            else:
                raise RuntimeError(f"readable_file:{path} is not a valid to a file")
        return os.path.abspath(path)

    def run_smarts(self):
        """
        | This runs the SMARTS batch script. This has some quirks as a legacy
        | program. Files will have to be switched back and forth while the
        | working directory is held constant.

        Parameters
        ----------
        """
        # Get all inp files
        inplist = glob(self.pwd + "/data/smarts_inp/" + self.runid + "_*.inp.txt")
        inplist.sort()
        if self.log: self.log.debug(f"all inp files: {inplist}")

        # Clear out any old files
        try:
            os.remove(self.pwd + "/SMARTS/smarts295.out.txt")
        except FileNotFoundError:
            pass
        try:
            os.remove(self.pwd + "/SMARTS/smarts295.ext.txt")
        except FileNotFoundError:
            pass
        try:
            os.remove(self.pwd + "/SMARTS/smarts295.scn.txt")
        except FileNotFoundError:
            pass

        self.outarray = []

        # Change working directory to SMARTS
        os.chdir(self.pwd + "/SMARTS/")
        try:
            # Cycle through input files
            for inp in inplist:
                #TODO this is linux-only currently
                fileid = inp.split('/')[-1].split(".inp.txt")[0]
                try:
                    self.file_path(inp)
                except RuntimeError:
                    self.outarray.append(-1)
                    continue
                shutil.copyfile(inp, self.pwd + "/SMARTS/smarts295.inp.txt")

                #TODO this is linux-only right now.
                subprocess.run(self.pwd + "/SMARTS/smarts295bat")
                with open(self.pwd + "/SMARTS/smarts295.out.txt", 'r', encoding="ISO-8859-1") as outfile:
                    found = False
                    zenith = False
                    turbid = False
                    for row in outfile:
                        if "Terrestrial = " in row:
                            irr = row.split('=')[2].replace(' ', '').split('A')[0]
                            self.outarray.append(irr)
                            if self.log: self.log.info(f"Calculated IRR={irr} successfully.")
                            found = True
                        elif "> 90 deg. RUN ABORTED!" in row:
                            zenith = True
                            if self.log: self.log.info(f"Zenith angle low, nighttime.  Setting to -2")
                        elif "turbidity is too large" in row:
                            turbid = True
                            if self.log: self.log.info(f"Turbidity problem in file, setting to -3")
                    if found == False:
                        if zenith == True:
                            self.outarray.append(-2)
                        elif turbid == True:
                            self.outarray.append(-3)
                        else:
                            self.outarray.append(-4)
                    # Move these files into our output storage space
                    try:
                        shutil.move(self.pwd + "/SMARTS/smarts295.out.txt", \
                        self.pwd + "/data/smarts_out/" + fileid + ".out.txt")
                    except FileNotFoundError:
                        pass
                    try:
                        shutil.move(self.pwd + "/SMARTS/smarts295.ext.txt", \
                        self.pwd + "/data/smarts_out/" + fileid + ".ext.txt")
                    except FileNotFoundError:
                        pass
                    try:
                        shutil.move(self.pwd + "/SMARTS/smarts295.scn.txt", \
                        self.pwd + "/data/smarts_out/" + fileid + ".scn.txt")
                    except FileNotFoundError:
                        pass
        finally:
            # Return to original working directory
            os.chdir(self.pwd)
            if self.log: self.log.info(f"Done with SMARTS loop")
            if self.log: self.log.debug(f"Output array: {self.outarray}")
            with open(self.pwd + "/SMARTS_irr.csv", 'w') as outfile:
                outfile.write("SMARTSirr\n")
                for entry in self.outarray:
                    outfile.write(str(entry))
                    outfile.write('\n')
            if self.log: self.log.info(f"Saved as {self.pwd + "SMARTS_irr.csv"}")
