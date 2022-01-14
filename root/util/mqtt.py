#!/usr/bin/env python3

import threading
from bot_util.helper.bot_status import update_status
from bot_util.helper.mqtt.consumer import listen_for_status_change
from paho.mqtt.client import MQTTMessage
from root.contants.constant import MQTT_TOPIC_NAME
import root.util.logger as logger


def on_message(client, userdata, msg: MQTTMessage):
    logger.info(
        "Received message: [%s] of type [%s]" % (msg.payload, type(msg.payload))
    )
    status: str = msg.payload.decode("utf-8").lower()
    update_status(status)


def mqtt_listener():
    if MQTT_TOPIC_NAME == "missing_topic_name":
        logger.error("Missing MQTT_TOPIC_NAME in environment")
        # TODO: log it to the channel
        return
    logger.info("Starting mqtt listener")
    t: threading.Thread = threading.Thread(
        target=listen_for_status_change, args=(MQTT_TOPIC_NAME, on_message)
    )
    t.start()
