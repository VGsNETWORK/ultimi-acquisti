#!/usr/bin/env python3

from os import environ
import threading
from bot_util.helper.bot_status import update_status
from bot_util.helper.mqtt.consumer import listen_for_status_change
from paho.mqtt.client import MQTTMessage
from root.contants.constant import MQTT_TOPIC_NAME
from bot_util.constant.maintenance import MAINTENANCE_BOT_CODE
import root.util.logger as logger
from bot_util.handler.maintenance import send_update_status_message


def on_message(client, userdata, msg: MQTTMessage):
    logger.info(
        "Received message: [%s] of type [%s]" % (msg.payload, type(msg.payload))
    )
    status: str = msg.payload.decode("utf-8").lower()
    update_status(MAINTENANCE_BOT_CODE, status)
    # TODO: MAINTENANCE_BOT_CODE can be used in the library
    # TODO: BOT_NAME: can be retrieved from the environment BOT_NAME
    try:
        send_update_status_message(
            "#ultimiacquisti", "@UltimiacquistiBot", MAINTENANCE_BOT_CODE, status
        )
    except Exception as e:
        logger.error(e)


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
