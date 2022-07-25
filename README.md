# moxaiiot-ble-mqtt-connector
Connect BLE sensors to Mosquitto Broker 

# deploy container:
docker run -d --net=host --name bluetooth --privileged  amjadbadar05/mx-ble-mqtt:0.0.2-armhf

# start an interactive bash shell inside your running container
sudo docker exec -it bluetooth "bash"

# Payload 
![image](https://user-images.githubusercontent.com/22453359/180788227-a2879895-5114-4010-b4de-94594d73d3cf.png)
