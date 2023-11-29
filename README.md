# moxaiiot-ble-mqtt-connector
Connect BLE sensors to local Mosquitto MQTT Broker. Current implementation read BLE beacons in disconnected mode that means sensors do not need to connect to BLE controller all the time. 
The following BLE sensor essentim SPOT is integrated. In principle the source code can recieve ble sensor data from any other ble sensors as well. 
https://essentim.com/en/essentim-sensors

![image](https://github.com/abadar05/ble-to-mqtt-container/assets/22453359/faddefd8-f30c-4089-8748-da979bb8a83c)


# Prequisites:
- Local MQTT Broker running as docker container or systemd service
  - sudo apt-get install mosquitto 
  - sudo systemctl status mosquitto

## Deploy container via CLI:
- The --cpus=<value> option specify how much of the available CPU resources a container can use. 
  Example the following command limit the container at most 10% of the CPU every second.
  
 - The --memory=<value> option specify maximum amount of memory the container can use. If you set this option, the minimum allowed value is 6m (6 megabytes). 
  
  ```
  sudo docker run -d \
   --net=host \
   --name bluetooth --privileged \
   --cpus=".1" --memory="20m" \
   --restart=always \
   --log-driver json-file amjadbadar05/mx-ble-mqtt:0.0.4-armhf --ipv4="127.0.0.1"
   
   ```
## Deploy container via docker-compose:
 ```
  docker-compose up
 ```
- OUTPUT
  As you can see bluetooth application is connected successfully to local mosquitto broker 
![image](https://github.com/abadar05/ble-to-mqtt-container/assets/22453359/85845ba3-d051-4ba9-918e-891f553f3dab)
 


- Verify conatiner is running
![image](https://github.com/abadar05/ble-to-mqtt-container/assets/22453359/e3476fa4-518a-41d2-a6b0-d3d2bbaf0ed9)

 
- Verify container logs
- sudo docker container logs bluetooth 
![image](https://github.com/abadar05/ble-to-mqtt-container/assets/22453359/a6fc818d-254b-4172-859a-729bc6b8bbd4)


# start an interactive bash shell inside your running container in order to change the configuration 
sudo docker exec -it bluetooth "bash"
  
![image](https://user-images.githubusercontent.com/22453359/194760054-1f1f5f80-ab0b-403e-8ce7-a22c7ca4cd23.png)
 
# Payload 
![image](https://user-images.githubusercontent.com/22453359/180788227-a2879895-5114-4010-b4de-94594d73d3cf.png)
