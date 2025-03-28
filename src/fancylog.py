#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WTH custom logging class
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




class FancyLog():
    """
    | Nested class which provides fancy options for logging as a oneliner in main
    """

    import logging
    from datetime import datetime

    loglvl = None
    makelog = None
    filename = "/dev/null"
    logpath="./"

    def __init__(self, loglvl=logging.INFO, makelog=False, logpath=None):
        """
        | Init the MyLog Class

        Parameters
        ----------
        loglvl : int
            Integer used by logging to determine the log level.  Defaults to INFO.
            Accepts strings.
        makelog : bool
            Should this make an optional output file in addition to stdout?
        logpath : str
            What directory should the file be saved at?
        """
        self.loglvl = loglvl
        self.makelog = makelog
        self.logpath = logpath
        return

    def run(self):
        """
        | Create log instance with file saving and color stdout.

        Returns
        -------
        logger : Object
            logging object similar to the original import
        """
        # create logger with file name
        logger = self.logging.getLogger(__file__)
        logger.setLevel(self.logging.DEBUG)

        # create console handler with a higher log level
        lch = self.logging.StreamHandler()
        lch.setLevel(self.loglvl)
        # Apply our settings
        lch.setFormatter(self.LogFormatterColors())
        logger.addHandler(lch)

        # create logfile handler with a higher log level
        if self.makelog:
            if self.logpath != None:
                if self.logpath[-1] != '/':
                    self.logpath += '/'
                self.filename = self.logpath
            else:
                self.filename = "./"
            self.filename += "log-" + str(self.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + ".log"
            lfh = self.logging.FileHandler(self.filename)
            lfh.setLevel(self.loglvl)
            # Apply settings without color
            lfh.setFormatter(self.LogFormatterBoring())
            logger.addHandler(lfh)
        logger.info("Loaded FancyLog")
        if self.makelog:
            logger.info(f"Logfile saved at {self.logpath}{self.filename}")

        return logger

    class LogFormatterColors(logging.Formatter):
        """
        | This class creates colorful terminal outputs for log files.  Requires logging.

        Parameters
        ----------
        logging.Formatter : logging.Formatter object
            Object function pass
        """
        import logging
        # Color list, terminal format
        grey = "\x1b[38;20m"
        cyan = "\x1b[0;36m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        panic_red = "\x1b[0;41m"
        reset = "\x1b[0m"

        strformat = "%(asctime)s,%(name)s,%(levelname)s,%(message)s,line:%(lineno)d"
        FORMATS = {
            logging.DEBUG: cyan + strformat + reset,
            logging.INFO: grey + strformat + reset,
            logging.WARNING: yellow + strformat + reset,
            logging.ERROR: red + strformat + reset,
            logging.CRITICAL: panic_red + strformat + reset
        }

        def format(self, record):
            """
            Picks the format based on the loglevel int and emits that format.

            Parameters
            ----------
            record : logging.LogRecord object
                stores the information from the log input when attached via call.
            """
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = self.logging.Formatter(log_fmt)
            return formatter.format(record)

    class LogFormatterBoring(logging.Formatter):
        """
        | This class creates standard outputs for logger which behaves like
        | LogFormatterColors.  Requires logging.

        Parameters
        ----------
        logging.Formatter : logging.Formatter object
            Object function pass
        """
        import logging
        strformat = "%(asctime)s,%(name)s,%(levelname)s,%(message)s,line:%(lineno)d"
        FORMATS = {
            logging.DEBUG: strformat,
            logging.INFO: strformat,
            logging.WARNING: strformat,
            logging.ERROR: strformat,
            logging.CRITICAL: strformat
        }

        def format(self, record):
            """
            Picks the format based on the loglevel int and emits that format.

            Parameters
            ----------
            record : logging.LogRecord object
                stores the information from the log input when attached via call.
            """
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = self.logging.Formatter(log_fmt)
            return formatter.format(record)
