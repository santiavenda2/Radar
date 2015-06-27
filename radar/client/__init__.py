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


from threading import Thread, Event
from json import loads as deserialize_json, dumps as serialize_json
from Queue import Empty as EmptyQueue
from ..network.client import Client
from ..protocol import Message


class RadarClientLite(Client):
    def __init__(self, *args, **kwargs):
        super(RadarClientLite, self).__init__(*args, **kwargs)
        self._message = Message()

    def on_receive(self):
        pass

    def send_message(self, message_type, message, message_options=Message.OPTIONS['NONE']):
        return self._message.send(self, message_type, message, message_options=message_options)

    def receive_message(self):
        return self._message.receive(self)


class RadarClient(RadarClientLite, Thread):

    NETWORK_MONITOR_TIMEOUT = 0.2
    RECONNECT_DELAYS = [5, 15, 60]

    def __init__(self, platform_setup, input_queue, output_queue):
        Thread.__init__(self)
        super(RadarClient, self).__init__(
            platform_setup.config['connect']['to'],
            platform_setup.config['connect']['port'],
            network_monitor_timeout=self.NETWORK_MONITOR_TIMEOUT,
            blocking_socket=False
        )
        self._logger = platform_setup.logger
        self._reconnect = platform_setup.config['reconnect']
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._delays = self.RECONNECT_DELAYS
        self.stop_event = Event()

    def _sleep(self):
        self.stop_event.wait(self._delays[0])
        self._delays.append(self._delays[0])
        self._delays.pop(0)

    def connect(self):
        while not self.is_stopped() and not self.is_connected():
            try:
                super(RadarClient, self).connect()
            except Exception, e:
                self._logger.log('Error - Can\'t connect to {:}:{:}. Details: {:}.'.format(self.address, self.port, e))

                if self._reconnect:
                    self._sleep()
                else:
                    self.stop_event.set()

    def on_receive(self):
        message_type, message = self.receive_message()
        self._output_queue.put_nowait({
            'message_type': message_type,
            'message': deserialize_json(message),
        })

    def on_timeout(self):
        try:
            serialized_message = serialize_json(self._input_queue.get_nowait())
            self.send_message(Message.TYPE['CHECK REPLY'], serialized_message)
        except EmptyQueue:
            pass

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        self.connect()

        while not self.is_stopped() and self.is_connected():
            # print 'here...'
            super(RadarClient, self).run()
            self.connect()

        # print 'terminating ...'