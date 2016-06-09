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
import queue
import time

from neblinaCommunication import NeblinaCommunication
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket

try:
    from bluepy.btle import *
except ImportError:
    raise ImportError("Unable to locate bluepy. It is a required module to use neblinaBLE API.")

###################################################################################

ServiceBatteryUUID = "0000180f-0000-1000-8000-00805f9b34fb"
ServiceBatteryDataUUID = "00002a19-0000-1000-8000-00805f9b34fb"

ServiceNeblinaUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaCtrlUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaDataUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class BLEDelegate(DefaultDelegate):

    def __init__(self):
        self.packets = queue.Queue()

    def handleNotification(self, cHandle, data):
        self.packets.put(data)
        logging.debug("handleNotification")

###################################################################################


class NeblinaBLE2(object):

    def __init__(self, address):
        NeblinaCommunication.__init__(self, address)
        self.connected = False
        self.delegate = BLEDelegate()
        self.peripheral = None

        self.serviceBattery = None
        self.readBatteryCh = None

        self.serviceNeblina = None
        self.writeNeblinaCh = None
        self.readNeblinaCh = None

    def connect(self):
        connected = False
        peripheral = None
        count = 0
        while not connected and count < 5:
            count += 1
            try:
                peripheral = Peripheral(self.address, "random")
                connected = True
                break
            except BTLEException as e:
                logging.warning("Unable to connect to BLE device, retrying in 1 second.")
            time.sleep(1)

        if connected:
            self.peripheral = peripheral
            self.connected = True

            self.serviceBattery = self.peripheral.getServiceByUUID(ServiceBatteryUUID)
            self.readBatteryCh = self.serviceBattery.getCharacteristics(ServiceBatteryDataUUID)[0]

            self.serviceNeblina = self.peripheral.getServiceByUUID(ServiceNeblinaUUID)
            self.writeNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaCtrlUUID)[0]
            self.readNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaDataUUID)[0]

            self.peripheral.withDelegate(self.delegate)
            self.enableNeblinaNotification()

    def disconnect(self):
        if self.connected:
            self.peripheral.disconnect()

    def isConnected(self):
        return self.connected

    def getBatteryLevel(self):
        if self.connected:
            bytes = self.readBattery()
            return bytes
        return None

    def readBattery(self):
        batteryLevel = self.readBatteryCh.read()
        return struct.unpack("<B", batteryLevel)[0]

    def receivedPacket(self):
        packet = None
        self.waitForNotification(0.01)
        try:
            data = self.delegate.packets.get(False)
            return data
        except queue.Empty:
            return None
        return None

    def sendPacket(self, packet):
        self.writeNeblinaCh.write(packet)

    def enableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle + 2, struct.pack('<bb', 0x01, 0x00))

    def disableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle + 2, struct.pack('<bb', 0x00, 0x00))

    def waitForNotification(self, timeout):
        return self.peripheral.waitForNotifications(timeout)