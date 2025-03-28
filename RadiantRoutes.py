#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RadiantRoutes solar irradiance calculator for migratory birds
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

# Default Packages
import argparse
import os
import pandas as pd
import sys

# Packages Imported by RRvenv

# Local Packages
from src.downloadAODVIIRS import downloadAODVIIRS
from src.procSMARTS import procSMARTS
# WTH custom logging class added in another file called "fancylog.py"
from src.fancylog import FancyLog


PWD = os.getcwd()
#TODO Populate this list further
DFHD = {\
    "dfyear": ["Year", "year", "YEAR", "yr", "YR", "YY", "YYYY"], \
    "dfmon": ["Month", "month", "MONTH", "mon", "MON", "MM"], \
    "dfday": ["Day", "day", "DAY"], \
    "dfhr": ["Hour", "hour", "HOUR"], \
    "dfmin": ["Minute", "minute", "MINUTE"], \
    "dfsec": ["Second", "second", "SECOND"], \
    "dflat": ["Latitude", "latitude", "LATITUDE", "track_latitude"], \
    "dflon": ["Longitude", "longitude", "LONGITUDE", "track_longitude"], \
    "dfseason": ["Season", "season", "SEASON"], \
    "dfasl": ["Asl", "asl", "ASL"], \
    "dfagl": ["Agl", "agl", "AGL"], \
    "dft": ["column_temperature"], \
    "dfrh": ["column_relhum"], \
    }

def in_venv(log=None):
    """
    | Check if we are in a virtual environment

    Parameters
    ----------
    log : Logging Object
        Logging object to print messages to a logfile
    """
    if sys.prefix == sys.base_prefix:
        if log: log.error(f"Not in a venv, source before running")
    else:
        if log: log.debug(f"confirmed we are in a venv")
    return

def check_import(checkme, log=None):
    """
    | Check that a module is imported.  Else raises a warning and attempts to
    | import the module in question.  Useful for checking other defs in code
    | generated from snippets.

    Parameters
    ----------
    checkme : string
        stringlike name of a module

    log : Logging Object
        Logging object to print messages to a logfile
    """
    import sys
    import importlib.util

    import_scoped_spec = importlib.util.find_spec(checkme)
    if import_scoped_spec is None:
        if log: log.error(f"{checkme} does not appear to be installed. Killing script.")
        raise ModuleNotFoundError(f"No import target for {checkme}.  Is it installed?")
    sys.exit(1)
    if checkme not in sys.modules:
        if log: log.warning(f"Module {checkme} is not imported.  Trying to fix.")
        if checkme in globals():
            if log: log.error(f"Module \"{checkme}\" namespace exists, can't import.  Exiting")
            raise ImportError(f"Module \"{checkme}\" namespace exists, can't import.  Exiting")
        sys.exit(1)
        globals()[checkme] = importlib.import_module(checkme)
        if log: log.info(f"Successfully loaded {checkme}")

        return

def arg_parsing():
    """
    | Container for command line arguments

    Returns
    -------
    args : argparse object
    """
    # argument parser
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__), \
        description='Automated solar irradiance for birds in flight', \
        epilog='', \
    )
    ## Input file
    parser.add_argument("infile", \
        type=arg_file_path, \
        help="Path to input csv file", \
    )
    # ## Input directory path; requires DEF-dir_path and os
    # parser.add_argument("inpath", type=arg_dir_path,\
    #     help="Path to *directory* files")
    # ## Output directory path; requires DEF-dir_path and os
    # parser.add_argument("-o", "--outpath", required=False, type=arg_dir_path,\
    #     help="Path to *directory* where we store output. Default=inpath")
    # ## Load optional config file; requires DEF-file_path and os
    # parser.add_argument("-c", "--config", required=False, type=arg_file_path,\
    #     help="Path to config file. Default=settings.ini")
    # ## Request user input date; requires "from datetime import datetime"
    # parser.add_argument("indate",\
    #     type=lambda xxx: datetime.strptime(xxx, "%Y-%m-%d"),\
    #         help="Input date with format YYYY-MM-DD")
    # ## Flag to plot data
    # parser.add_argument("-p", "--plot", action="store_true", required=False,\
    #     help="Plot output data")
    # ## Flag to skip to code position
    # parser.add_argument("-s", "--skip", action="store_true", required=False,\
    #     help="Skip processing and plot only")
    ## Flag for verbose logging; requires logging
    parser.add_argument("-v", "--verbose", default="warning", required=False,\
        help="Provide logging level. Options: [debug,info,warning,error,critical]" )
    ## Optional log to file; requires DEF-file_path and "from datetime import datetme"
    parser.add_argument("-l", "--logfile", \
        default=PWD + "/logs", \
        required=False, \
        type=arg_dir_path, \
        help="Path to store a log file.  Filename=log-YYYY-MM-DD_HH:MM:SS.log",\
    )

    # Parse everything we have and output
    args = parser.parse_args()
    return args

def arg_dir_path(path):
    """
    | Check that the os.path is actually a directory.  Else raises an error.

    Parameters
    ----------
    path : string
    stringlike path to check

    Returns
    -------
    path : string
    stringlike path
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
    if path[-1] != '/':
        path = path + '/'
        return path


def arg_file_path(path):
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
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"readable_file:{path} is not a valid to a file")
    return os.path.abspath(path)

def df_checker(indf, log=None):
    """
    | Check that the dataframe has all of the required info in the headers

    Parameters
    ----------
    indf : pd.DataFrame
        input dataframe to check
    log : Logging Object
        Logging object to print messages to a logfile
    """
    headers = list(indf.columns.values)
    if log: log.debug(f"all headers: {headers}")
    for key in DFHD.keys():
        matches = set(headers) & set(DFHD[key])
        if len(matches) > 1:
            if log: log.warning(f"DF header has more than one match for {matches}")
        elif len(matches) > 0:
            if log: log.debug(f"DF header match for {matches}")
        else:
            if log: log.error(f"DF header match not found from valid options in {DFHD[key]}, please check your input csv")
    return











def main():
    '''
    | Main is where the magic happens
    '''
    # Parse args
    args = arg_parsing()

    # create console handler with a higher log level
    logger = FancyLog(makelog=True, loglvl=args.verbose.upper(), logpath=PWD + "/logs").run()
    logger.debug("Loaded logging class")

    # Ensure the correct venv is loaded
    in_venv(log=logger)

    # Import the dataframe containing bird tracks
    indf = pd.read_csv(args.infile)
    # Confirm that the file has all of the info we need
    df_checker(indf, log=logger)

    # Load the SMARTS processor and create files
    procsmarts = procSMARTS(indf, DFHD, PWD, log=logger)
    procsmarts.create_inps()

    return


if __name__ == "__main__":
    main()


