# moxaiiot-ble-mqtt-connector
Connect BLE sensors to Mosquitto Broker 

# deploy container:
docker run -d --net=host --privileged  amjadbadar05/mx-ble-mqtt:0.0.2-armhf

# start an interactive bash shell inside your running container
sudo docker exec -it bluetooth "bash"
