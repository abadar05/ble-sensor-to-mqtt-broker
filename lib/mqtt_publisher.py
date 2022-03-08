#!/usr/bin/env python3
##
#   \copyright Moxa Europe 2021
"""
Publish BLE to json messages to Internal MQTT Mosquitto Broker 
"""

import time
import json
import ssl
import sys
import signal
import logging
import paho.mqtt.client as mqtt_client

__author__ = "Amjad B."
__license__ = "MIT"
__version__ = '1.0'
__status__ = "Experimental"

 
logger = logging.getLogger(__name__)

class MqttBaseCLass():
 
    def __init__(self, **kwargs):
          
        # Use parameters from external configuration   
        CONFIG = kwargs.get('conf', None)  
          
        self._client = None
        self._userdata = None
        self._mqqtconnect = None
        self.IS_CONNECTED = False
            
        self._broker_url = CONFIG._broker 
        self._port =  CONFIG._port
        #self._client_id = None
        self._clean_session = CONFIG._clean_session
        self._keep_alive_sec = CONFIG._keep_alive_sec
        self._topic = CONFIG._topic  
        
        """
        self._broker_url = "127.0.0.1" 
        self._port =  1883
        #self._client_id = None
        self._clean_session = True
        self._keep_alive_sec = 60
        self._topic = CONFIG._topic 
        """
        
    def init_mqtt_client(self):

        """
        Initilaize mqtt client configuration
        """
        logger.info("Create MQTT Client...")
        self._client = mqtt_client.Client(clean_session= self._clean_session, userdata=self._userdata)
        
        logger.info('Register Callback functions')
        
        self._client.on_connect = self.on_connect_callback
        self._client.on_disconnect = self.on_disconnect_callback
        self._client.on_publish = self.on_publish_callback
        self._client.on_message = self.on_message_callback
        self._client.on_subscribe = self.on_subscribe_callback
        self._client.on_log = self.on_log
              
        self._client.loop_start()
        
        return True    
        
    def connect_mqtt_broker(self):
        self._mqqtconnect = self._client.connect(host= self._broker_url, port= self._port, keepalive= self._keep_alive_sec)
        logger.info("Connecting to broker: {}".format(self._broker_url))
        
    def on_connect_callback(self, client, userdata, flags, rc):     
        logger.info('OnConnect! rc={}, flags={}'.format(rc, flags))     
        if rc == 0:           
            self.IS_CONNECTED = True
            logger.info("*************************************************************")
            logger.info("Connected successfully to Moxa internal broker: {}".format(self._broker_url))
            logger.info("*************************************************************")
            
        elif rc == 1:
            logger.error("Connection refused - incorrect protocol version, result code: {}".format(rc)) 
            self._client.loop_stop()
               
        elif rc == 2:
            logger.error("Connection refused - invalid client identifier, result code: {}".format(rc)) 
            self._client.loop_stop() 
             
        elif rc == 3:
            logger.error("Connection refused - server unavailable, result code: {}".format(rc)) 
            self._client.loop_stop()
            
        elif rc == 4:
            logger.error("Connection refused - bad username or password, result code: {}".format(rc))
            self._client.loop_stop()
            
        else:
            logger.error("Connection refused - not authorised, result code: {}".format(rc)) 
            self._client.loop_stop()
            
                      
    def on_disconnect_callback(self, client, userdata, rc):
        logger.info('OnDisonnect! rc = %s', rc)
        self.IS_CONNECTED = False
        if rc:
            logger.error('Disonnected with result code = {}'.format(rc))  
        return

    def on_log(self, client, userdata, level, buf):
        logger.info("OnLog(%s): %s ", level, buf)
        return
        
    def on_publish_callback(self, client, userdata, mid):
        logger.debug('OnPublish MsgID [%s]', mid)
        
    def on_subscribe_callback(self, client, obj, mid, granted_qos):
        logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))
        
       
    def on_message_callback(self, client, obj, msg):
        logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        
        output = self._read_lf(msg)
        logger.info("MQTT Message: {}".format(output))
          
    def is_open(self):
        if self._client and self.IS_CONNECTED == True:
            return True
        else:
            return False