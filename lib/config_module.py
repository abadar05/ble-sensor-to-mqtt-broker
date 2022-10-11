#!/usr/bin/env python3

##
#   \copyright Moxa Europe 2021

"""
# Change log

Date: 25 Nov 2021: 
    - Disabled colored log 
    - Disabled log into logfile 
    - Change getLogger name to app 
"""

import sys
import logging
from colorlog import ColoredFormatter

__author__ = "Amjad B"
__license__ = "MIT"
__version__ = '1.1'
__status__ = "Experimental"


class Config_BaseClass():
    global logger
    mainFHandler = "Not initiated"
    errorFHandler = "Not initiated"
    
    def __init__(self, args, **kwargs):
        ##
        # Default configuration will be loaded if not specified in config file
        
        #self._client = None
        self._broker = "127.0.0.1"
        self._port = 502        
        self._clean_session = True
        self._keep_alive_sec = 60
        self._topic = "/Moxa/BLE/"
        
        self._maclist = ["AA:BB:CC:DD:EE:FF"]
        self._hci_device_id = 0
        self._publish_all_ble_advertise = False    
        
        self._ext_conf = kwargs.get('conf', None)
        self._verbose_level = "default"
        #override default logger level if comes via command line
        if args.verbose_level is not None:
            if args.verbose_level == '1': # enable only warning messages 
                self._verbose_level = args.verbose_level
            elif args.verbose_level == '2': 
                self._verbose_level = args.verbose_level
            else:
                print("[ERROR] Invalid Verbose Level: {}. Please use -h argument to see usage".format(args.verbose_level)) 
                sys.exit()
        
        ##
        # from now we can start to write logs in the file
              
        self.set_loggingFileHandler() # initiate logging to File
        #self.set_loggingFileHandler("info.log", 'error.log') # initiate logging to File
        
        logger = logging.getLogger("app")
        logger.debug("Read External Config: {}".format(self._ext_conf))    
        self.parse_configuration(args)
           
    # Parse config.json file        
    def parse_configuration(self, args):
        logger = logging.getLogger("app")
        
        logger.info("*********** Parse Configuration ***********")
        if not self._ext_conf:
            logger.error('Empty configuration!')
            return False          
        # continue here 
        if self._ext_conf["mqtt"]["broker"]: 
            self._broker = self._ext_conf["mqtt"]["broker"]
            if args.IP is not None:     #override IP from config file if comes via command line
                 self._broker = args.IP
            logger.info("broker: {}".format(self._broker))
        
        if self._ext_conf["mqtt"]["port"]: 
            self._port = self._ext_conf["mqtt"]["port"]
            logger.info("port: {}".format(self._port))
            
        if self._ext_conf["mqtt"]["clean_session"]: 
            self._clean_session = self._ext_conf["mqtt"]["clean_session"]
            logger.info("clean_session: {}".format(self._clean_session))
            
        if self._ext_conf["mqtt"]["keep_alive_sec"]: 
            self._keep_alive_sec = self._ext_conf["mqtt"]["keep_alive_sec"]
            logger.info("keep_alive_sec: {}".format(self._keep_alive_sec))
        
        if self._ext_conf["mqtt"]["topic"]: 
            self._topic = self._ext_conf["mqtt"]["topic"]
            logger.info("topic: {}".format(self._topic))
            
        if self._ext_conf["ble_sensors"]["maclist"]: 
            self._maclist = self._ext_conf["ble_sensors"]["maclist"]
            logger.info("maclist: {}".format(self._maclist))    
            
        if self._ext_conf["ble_controller"]["hci_device_id"]: 
            self._hci_device_id = self._ext_conf["ble_controller"]["hci_device_id"]
            logger.info("hci_device_id: {}".format(self._hci_device_id))        
            
        if self._ext_conf["ble_controller"]["publish_all_ble_advertise"]: 
            self._publish_all_ble_advertise = self._ext_conf["ble_controller"]["publish_all_ble_advertise"]
            logger.info("publish_all_ble_advertise: {}".format(self._publish_all_ble_advertise))      
              
        logger.info("**** Parse Configuration Successfull! ****")
        return True 
    
    # logging configuration
    def set_loggingFileHandler(self): 
    #def set_loggingFileHandler(self, mainlog, errorlog):  
        """
        From now display logs on console in colored output
        """
        log_format = '%(asctime)s: %(levelname)s - %(name)s - xx %(message)s'
        # Save full log
        
        #logging.basicConfig(level=logging.DEBUG, datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format, filename=mainlog, filemode = "w")
        color_format = ColoredFormatter("%(asctime)s: %(log_color)s %(levelname) - 2s%(reset)s - %(name)s - %(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
            reset = False,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',})
        
        logger = logging.getLogger("app")
        console = logging.StreamHandler() 
        
        if self._verbose_level == '1':
            #console.setLevel(logging.WARN)
            logging.basicConfig(level=logging.WARN, datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format)
            logger.info("Enabled Warning Mode: {}".format(self._verbose_level))
        elif self._verbose_level == '2':
            #console.setLevel(logging.DEBUG)
            logging.basicConfig(level=logging.DEBUG, datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format)
            logger.info("Enabled Debug Mode: {}".format(self._verbose_level))  
        else:
            #console.setLevel(logging.INFO)
            logging.basicConfig(level=logging.INFO, datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format)
        
        #console.setFormatter(color_format) 
        #logging.getLogger("app").addHandler(console)
        
        """
        # Save error log
        global errorFHandler
        errorFHandler = logging.FileHandler(errorlog)
        errorFHandler.setLevel(logging.ERROR)
        formatter = logging.Formatter(log_format)
        errorFHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(errorFHandler)   
        """
