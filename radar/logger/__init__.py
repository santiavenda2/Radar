# -*- coding: utf-8 -*-

"""
This file is part of Radar.

Radar is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Radar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Lesser GNU General Public License for more details.

You should have received a copy of the Lesser GNU General Public License
along with Radar. If not, see <http://www.gnu.org/licenses/>.

Copyright 2015 Lucas Liendo.
"""


from logging import getLogger, Formatter, shutdown, INFO
from logging.handlers import RotatingFileHandler
from os.path import dirname
from os import mkdir
from errno import EEXIST


class LoggerError(Exception):
    pass


class RadarLogger(object):
    def __init__(self, path, logger_name='radar'):
        self._create_dir(dirname(path))
        self.logger = self._configure_logger(path, logger_name)

    def _create_dir(self, path):
        try:
            mkdir(path)
        except OSError, e:
            if e.errno != EEXIST:
                raise LoggerError('Error - Couldn\'t create directory : {:}. Details : {:}.'.format(path, e.strerror))

    def _configure_logger(self, path, logger_name):
        logger = getLogger(logger_name)
        logger.setLevel(INFO)
        file_handler = RotatingFileHandler(path, maxBytes=10 * 1024 * 1024, backupCount=10)
        formatter = Formatter(fmt='%(asctime)s - %(message)s', datefmt='%b %d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def log(self, message):
        self.logger.info(message)

    def shutdown(self):
        shutdown()
