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


from ..config.server import ServerConfig
from . import LinuxSetup


class SetupError(Exception):
    pass


class LinuxServerSetup(ServerConfig, LinuxSetup):

    BASE_PATH = '/etc/radar/server'
    PLATFORM_CONFIG_PATH = BASE_PATH + '/config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '/radar.yml'
    PLATFORM_CONFIG = ServerConfig.DEFAULT_CONFIG
    PLATFORM_CONFIG.update({
        'checks': PLATFORM_CONFIG_PATH + '/checks',
        'contacts': PLATFORM_CONFIG_PATH + '/contacts',
        'monitors': PLATFORM_CONFIG_PATH + '/monitors',
        'plugins': '/usr/local/radar/server/plugins',
        'pidfile': '/var/run/radar/server.pid',
        'log file': '/var/log/radar/server.log',
    })

    def _configure_plugins(self):
        [p.configure(self.logger) for p in self.plugins]

    def _shutdown_plugins(self):
        [p.on_shutdown() for p in self.plugins]

    def configure(self, launcher):
        super(LinuxServerSetup, self).configure()
        self._configure_plugins()
        self._write_pid_file(self.config['pidfile'])
        self._install_signal_handlers(launcher)
        self._switch_process_owner(self.config['run as']['user'], self.config['run as']['group'])

    def tear_down(self, launcher):
        self._delete_pid_file(self.config['pidfile'])
        self._shutdown_plugins()
        super(LinuxServerSetup, self).tear_down()


class WindowsServerSetup(ServerConfig):

    BASE_PATH = 'C:\\Program Files\\Radar\\Server'
    PLATFORM_CONFIG_PATH = BASE_PATH + '\\Config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '\\radar.yml'
    PLATFORM_CONFIG = ServerConfig.DEFAULT_CONFIG
    PLATFORM_CONFIG.update({
        'checks': PLATFORM_CONFIG_PATH + '\\Checks',
        'contacts': PLATFORM_CONFIG_PATH + '\\Contacts',
        'monitors': PLATFORM_CONFIG_PATH + '\\Monitors',
        'plugins': PLATFORM_CONFIG_PATH + '\\Plugins',
        'log file': BASE_PATH + '\\Log\\server.log'
    })