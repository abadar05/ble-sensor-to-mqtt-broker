#!/usr/bin/env python3

##
#   \copyright Moxa Europe 2021

"""
Simple BLE forever-scan example, that prints all the detected
LE advertisement packets, and publish into local mosquitto mqtt broker
"""

"""
# Change log

Date: 25 Nov 2021: 
    - Change getLogger name to app in main()
"""

import sys
import struct
import binascii
import logging
import time 
import json 
from socket import htons
from lib.mqtt_publisher import MqttBaseCLass
from lib.config_module import Config_BaseClass
import threading
import queue
from collections import deque
   
import bluetooth._bluetooth as bluez
from lib.bluetooth_utils import (toggle_device,
                             enable_le_scan, parse_le_advertising_events,
                             disable_le_scan, raw_packet_to_str)

__author__ = "Amjad B."
__license__ = "MIT"
__version__ = '1.1'
__status__ = "Experimental"

logger = logging.getLogger("app")

def init_bluez_dev(hciX=None):
    
    if hciX is not None:
        dev_id = hciX
    else:    
        dev_id = 0  # the bluetooth device is hci0
    try:
        toggle_device(dev_id, True)
    except OSError as error:
        logger.error("No such hci device found with device id: {}".format(dev_id))  
        sys.exit(0)    
    try:
        sock = bluez.hci_open_dev(dev_id)
    except:
        logger.error("Cannot open bluetooth device %i" % dev_id)
        raise
    enable_le_scan(sock, filter_duplicates=False)
    return sock
   
def recv_ble_adv(mqtt, incoming_msg_deque, hciX):

    sock = init_bluez_dev(hciX)
    try:
        def le_advertise_packet_handler(mac, adv_type, data, rssi):
                 
            # Get advertisement for all other BLE sensors
            data_str = raw_packet_to_str(data)
            logger.debug("[Recv] Raw BLE Advertise: %s %02x %s %d" % (mac, adv_type, data_str, rssi))
            payload = {"timestamp": None, "mac": None, "adv_type": None, "data": None, "RSSI": None}
            payload["timestamp"] = int(time.time()*1000)  
            payload["mac"] = mac
            payload["adv_type"] = adv_type
            payload["data"] = data
            payload["RSSI"] = rssi
            incoming_msg_deque.append(payload) 
            #print("Queue Length", (incoming_msg_deque.maxlen))
        # Blocking call (the given handler will be called each time a new LE
        # advertisement packet is detected)
        parse_le_advertising_events(sock,
                                    handler=le_advertise_packet_handler,
                                    debug=False)              
    except KeyboardInterrupt:
        disable_le_scan(sock)


def word2int(data):
    # return int
    if type(data) == bytes:
        output = struct.unpack(">H", data)
        return output[0]
    else:
        return False


def ble_to_mqtt(mqtt, payload):

    if payload is not None:
        # Publish to internal MQTT broker 
        mqtt_connection = mqtt.is_open() 
        if mqtt_connection is not False:
            logger.info("Mqtt Connection OPEN! {}".format(mqtt_connection)) 
            payload = json.dumps(payload)
            mqtt._client.publish(mqtt._topic, (payload)) 
            logger.info("[Publish] = {}".format(payload))
        else:    
            logger.error("Mqtt Connection CLOSED! {}".format(mqtt_connection))

def read_ext_config(args):
        """
        Configuration
        """
        config_file = args.config_file
        if args.config_file is None:
             config_file = 'config.json'
        try:
            with open(config_file) as json_data_file:
                cfg_obj = json.load(json_data_file)
                logger.debug("Read External Config: {}".format(cfg_obj)) 
                return cfg_obj
        except IOError as e:
            logger.error(e)

def main_argparse(assigned_args = None):  
    """
    Parse and execute the call from command-line.
    Args:
        assigned_args: List of strings to parse. The default is taken from sys.argv.
    Returns: 
        Namespace list of args
    """
    import argparse, logging
    #parser = argparse.ArgumentParser(prog="appcmd", description=globals()['__doc__'], epilog="!!Note: .....")
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="config_file", metavar="<Config File>. If not provided explicitly default config.json will be used", help="Configuration file to use!")
    parser.add_argument("--ipv4", dest="IP", metavar="<Broker IP>. Default ['127.0.0.1']", type=str, help="Overwrite Broker IP!")
    parser.add_argument("-v", "--verbose", dest="verbose_level", default=None, help="Turn on console DEBUG mode [-v 2]")
    parser.add_argument("-V", "--version", action="version", version=__version__) 
    return parser.parse_args(assigned_args)


def process_ble_adv(mqtt, incoming_msg_deque, config=None):

    """
    Essentim BLE advertise decoding 
    0xA0 : Battery Level (0x64 means 100%)
    0x01 : Temperature (0xB409 means 0x09B4 readable, means 2484 decimal means 24,84°C)
    0x02 : Motion Señor (0x01 means in motion, 0x00 means no motion)
    0x03 : Door State Sensor (0x01 means open, 0x00 means closed) … 
    """
    
    # default is disable 
    publish_all_ble_advertise = False
    if config is not None:
        publish_all_ble_advertise = config._publish_all_ble_advertise 
    while True:
        if len(incoming_msg_deque) != 0:
            time.sleep(0.05)
            payload = incoming_msg_deque.popleft()  
            timestamp = payload["timestamp"] 
            mac = payload["mac"] 
            adv_type = payload["adv_type"]
            rssi = payload["RSSI"]
            data = payload["data"]
            data_str = raw_packet_to_str(data)
            
            # data_str = raw_packet_to_str(data)
            if publish_all_ble_advertise:
                payload["data"] = data_str
                # Publish all BLE advertisements to mosquitto broker
                ble_to_mqtt(mqtt, payload) 
                   
            # Allow only specified essentim sensors advertisements into the system based on MAC 
            # and decode the raw byte stream, construct the payload and publish to mosquitto broker 
            getMacList = config._maclist
            if getMacList is not None:
                getMacDict = {key: None for key in getMacList}
                if mac in getMacDict:
                    if len(data) == 25:
                        logger.info("*************************************************************")
                        logger.info("[Recv] essentim BLE Advertise: %s adv_type=%02x data=%s RSSI=%d" % (mac, adv_type, data_str, rssi))
                        logger.info("*************************************************************")
        
                        battery_event_id = data[16]
                        battery_event_value = data[17]
                        logger.debug("[Decoded] essentim BLE Advertise: {} BatteryLevelEventID {} Value {}".format(mac, hex(battery_event_id), battery_event_value))  
                        
                        temperature_sensor_id = data[18]
                        temperature_sensor_value = data[19:21]
                        temperature_sensor_value = htons(word2int(temperature_sensor_value))
                        logger.debug("[Decoded] essentim BLE Advertise: {} TemperatureSensorID {} Value {}".format(mac, hex(temperature_sensor_id), temperature_sensor_value*0.01))  
                        
                        motion_sensor_id = data[21]
                        motion_sensor_value = data[22]
                        logger.debug("[Decoded] essentim BLE Advertise: {} MotionSensorID {} Value {}".format(mac, hex(motion_sensor_id), (motion_sensor_value)))  
                        
                        door_state_sensor_id = data[23]
                        door_state_sensor_value = data[24]
                        logger.debug("[Decoded] essentim BLE Advertise: {} DoorStateSensorID {} Value {}".format(mac, hex(door_state_sensor_id), (door_state_sensor_value)))  
                        
                        # GET Sequence number
                        sequence_number = data[6:8]
                        # print(binascii.hexlify(sequence_number))
                        swap_byte_order = htons(word2int(sequence_number))
                        # print(swap_byte_order)
            
                        ## build BLE to JSON
                        # payload = {"sensor:" sensorMAC, "timestamp": systemUnix, "RSSI": -56, "metrics":[{key:value}]}
                        
                        payload = {"sensor": None, "timestamp": None, "RSSI": None, "metrics":None}
                        metricList = []
                        payload["sensor"] = mac
                        payload["timestamp"] = timestamp 
                        payload["RSSI"] = rssi
                        
                        battery_event = {"BatteryLevel": battery_event_value}
                        metricList.append(battery_event)
                        temperature_event = {"Temperature": temperature_sensor_value*0.01}
                        metricList.append(temperature_event)   
                        motion_event = {"MotionState": motion_sensor_value}
                        metricList.append(motion_event) 
                        door_event = {"DoorState": door_state_sensor_value}
                        metricList.append(door_event) 
                            
                        payload['metrics'] = metricList
                        # Publish essentim BLE advertisements to mosquitto broker 
                        ble_to_mqtt(mqtt, payload)
                else:
                    pass
       

def main(assigned_args = None):

    #global logger
    logger = logging.getLogger("app")
    
    cargs = main_argparse(assigned_args) # parse command line parameter
    obj_ext_configuration = read_ext_config(cargs) # create configuration object which contains all File Information from configuraiton file
    CONFIG = Config_BaseClass(cargs, conf=obj_ext_configuration) # parse configuration file to create related program variables in the configuration_object
   
    ## Initialize MQTT
    mqtt = MqttBaseCLass(conf=CONFIG)
    mqtt.init_mqtt_client()
    mqtt.connect_mqtt_broker()
     
    #Initialize queue object
    incoming_msg_deque= deque(maxlen=100)
    
    try:     
        recvBLEThread = threading.Thread(target=recv_ble_adv, args=(mqtt, incoming_msg_deque, CONFIG._hci_device_id,))
        recvBLEThread.start()
        logger.info("************************")
        logger.info("Recv BLE Thread Started!")
        logger.info("************************")
        
        mqttBLEThread = threading.Thread(target=process_ble_adv, args=(mqtt, incoming_msg_deque, CONFIG,))
        mqttBLEThread.start()
        logger.info("***************************")
        logger.info("BLE to MQTT Thread Started!")
        logger.info("***************************")
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        # Clean up the connection
        recvBLEThread.join()
        mqttBLEThread.join()
        sys.exit(0)   

if __name__ == '__main__':
    main()
    
   
