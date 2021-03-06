#!/usr/bin/env python
###################################################################################
#
# Copyright (c)     2010-2016   Motsai
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###################################################################################

import logging
import time
import unittest

from test.integration.baseIntegrationTest import BaseIntegrationTest
from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


def getSuite(comPort):
    UARTIntegrationTest.comPort = comPort
    return unittest.TestLoader().loadTestsFromTestCase(UARTIntegrationTest)

###################################################################################


class UARTIntegrationTest(BaseIntegrationTest):
    setupHasAlreadyRun = False
    comPort = None

    def setUp(self):
        if not self.comPort:
            raise unittest.SkipTest("No COM port specified.")

        # Give it a break between each test
        time.sleep(1)

        if not self.setupHasAlreadyRun:
            self.api = NeblinaAPI(Interface.UART)
            self.api.open(self.comPort)
            if not self.api.isOpened():
                self.fail("Unable to connect to COM port.")
            self.api.streamDisableAll()
            self.api.sessionRecord(False)
            self.api.setDataPortState(Interface.UART, True)

    def tearDown(self):
        self.api.streamDisableAll()
        self.api.sessionRecord(False)
        self.api.close()
        pass

