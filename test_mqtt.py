import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


Host = "m12.cloudmqtt.com"
Port = 19701
ClientId = "wuquiups2"
Topic = "idelect"
Auth = {"username":"idelect1", "password":"idelect1"}


publish.single(Topic, "msg",qos=0, hostname=Host, port=Port, client_id=ClientId, auth = Auth)
