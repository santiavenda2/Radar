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


from unittest import TestCase
from ..misc import SequentialIdGenerator


class TestSequentialIdGenerator(TestCase):
    def test_ids_are_unique(self):
        generator_a = SequentialIdGenerator()
        generator_b = SequentialIdGenerator()
        self.assertNotEqual(generator_a.generate(), generator_b.generate())
        self.assertNotEqual(id(generator_a), id(generator_b))
