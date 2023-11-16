from sml_block_maper import SmlEntry
from typing import List
import json
import logging

try:
    import paho.mqtt.client as mqtt
except ImportError:
    logging.error("paho.mqtt package not found")


class WriteData(object):
    def __init__(self):
        super().__init__()

    def writeData(self, data: List[SmlEntry]):
        for dataItem in data:
            print(json.dumps(dataItem.__dict__))


class MqttValue:
    def __init__(self, smlValue: SmlEntry):
        super().__init__()
        self.value = smlValue.value
        self.unit = smlValue.unit


class MqttDataWriter(WriteData):
    def __init__(self, urls: str, port: int, topic: str, qos: int):
        super().__init__()
        self.urls = urls
        self.port = port
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client()

    def createTopic(self, value: SmlEntry):
        return str(self.topic) + str(value.obis)

    def writeData(self, data: List[SmlEntry]):
        self.client.connect(self.urls, self.port)
        for dataItem in data:
            topic = self.createTopic(dataItem)
            dataAsJson = json.dumps(MqttValue(dataItem).__dict__)
            self.client.publish(topic, dataAsJson, qos=self.qos)
