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


from Queue import Empty as EmptyQueue
from abc import ABCMeta
from ctypes import cast, py_object
from functools import reduce
from threading import Thread, Event
from time import time
from ..misc import SequentialIdGenerator, RemoteControl
from ..protocol import Message


class ServerPluginError(Exception):
    pass


class ServerPlugin(RemoteControl):

    __metaclass__ = ABCMeta

    PLUGIN_NAME = ''
    PLUGIN_VERSION = '0.0.1'
    PLUGIN_CONFIG_FILE = None
    DEFAULT_CONFIG = {
        'enabled': True,
        'log runtime': False,
    }

    def __init__(self):
        if not self.PLUGIN_NAME:
            raise ServerPluginError('Error - Plugin name not defined.')

        self.id = SequentialIdGenerator().generate()
        self._logger = None
        self._message_actions = {
            Message.TYPE['CHECK REPLY']: self.on_check_reply,
            Message.TYPE['TEST REPLY']: self.on_test_reply,
        }

    def _log_runtime(self, elapsed_time):
        if self.log_runtime:
            self.log('Plugin {:} v{:} took {:.2f} seconds to run.'.format(self.PLUGIN_NAME, self.PLUGIN_VERSION, elapsed_time))

    def run(self, address, port, message_type, checks, contacts):
        start = time()

        try:
            action = self._message_actions[message_type]
            action(address, port, checks, contacts)
        except KeyError:
            self._logger.log('Unknown message id \'{:}\'.'.format(message_type))

        self._log_runtime(time() - start)

    def log(self, message):
        self._logger.log('Plugin {:} {:}. {:}'.format(self.PLUGIN_NAME, self.PLUGIN_VERSION, message))

    def configure(self, logger):
        self._logger = logger
        self.on_start()

    def on_start(self):
        """ Implement this method to initialize the plugin. """
        pass

    def on_check_reply(self, address, port, checks, contacts):
        """ Implement this method to process a check reply. """
        pass

    def on_test_reply(self, address, port, checks, contacts):
        """ Implement this method to process a test reply. """
        pass

    def on_shutdown(self):
        """ Implement this method to tear down the plugin. """
        pass

    def to_dict(self):
        return super(ServerPlugin, self).to_dict(['id', 'plugin_id', 'plugin_version', 'enabled'])

    def __eq__(self, other_plugin):
        return (self.PLUGIN_NAME == other_plugin.PLUGIN_NAME) and \
            (self.PLUGIN_VERSION == other_plugin.PLUGIN_VERSION)


class PluginManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2

    def __init__(self, platform_setup, queue):
        Thread.__init__(self)
        self._logger = platform_setup.logger
        self._plugins = platform_setup.plugins
        self._queue = queue
        self.stop_event = Event()

    # We dereference objects ids, to avoid re-instaintiating duplicate objects.
    def _dereference(self, ids):
        return [cast(object_id, py_object).value for object_id in ids]

    def _flatten(self, list_of_lists):
        return reduce(lambda l, m: l + m, list_of_lists)

    def _get_plugin_args(self, message):
        return (
            message['client_address'],
            message['client_port'],
            message['message_type'],
            self._flatten([c.as_list() for c in self._dereference(message['check_ids'])]),
            self._flatten([c.as_list() for c in self._dereference(message['contact_ids'])]),
        )

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        while not self.is_stopped():
            try:
                self._run_plugins(self._queue.get_nowait())
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)

    def _run_plugin(self, plugin, address, port, message_type, checks, contacts):
        try:
            plugin.run(address, port, message_type, checks, contacts)
        except Exception, e:
            self._logger.log('Error - Plugin \'{:}\' version \'{:}\' raised an error. Details : {:}.'.format(
                plugin.PLUGIN_ID, plugin.PLUGIN_VERSION, e))

    def _run_plugins(self, queue_message):
        plugin_args = self._get_plugin_args(queue_message)
        [self._run_plugin(p, *plugin_args) for p in self._plugins if p.enabled]
