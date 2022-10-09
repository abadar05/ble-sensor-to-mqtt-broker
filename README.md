# moxaiiot-ble-mqtt-connector
Connect BLE sensors to local Mosquitto MQTT Broker. Current implementation read BLE beacons in disconnected mode that means sensors do not need to connect to BLE controller all the time  

# Prequisites:
- Local MQTT Broker running as docker container or systemd service 
  - sudo apt-get install mosquitto 
  - sudo systemctl status mosquitto

# deploy container:
- The --cpus=<value> option specify how much of the available CPU resources a container can use. 
  Example the following command limit the container at most 10% of the CPU every second.
  
  - sudo docker run -d --net=host --name bluetooth --privileged --cpus=".1" amjadbadar05/mx-ble-mqtt:0.0.2-armhf

- Verify conatiner is running
![image](https://user-images.githubusercontent.com/22453359/194758641-704e863d-4828-4897-8209-7811e41f4c42.png)
 
- Verify container logs
- sudo docker container logs bluetooth 
![image](https://user-images.githubusercontent.com/22453359/194758698-3db21934-06f4-4881-9aea-5a2816ff9401.png)

# start an interactive bash shell inside your running container
sudo docker exec -it bluetooth "bash"

# Payload 
![image](https://user-images.githubusercontent.com/22453359/180788227-a2879895-5114-4010-b4de-94594d73d3cf.png)
