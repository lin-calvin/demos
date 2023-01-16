extends Node
class_name VccClient 
signal on_json
signal on_message

var json_resp
var uid=null
var connected=false
var client = WebSocketClient.new()
func _ready():
	client.connect("connection_closed", self, "closed")
	client.connect("connection_error", self, "closed")
	client.connect("connection_established", self, "connected")
	client.connect("data_received", self, "_on_data")
func _process(delta):
	client.poll()
func closed():
	print("closed")
signal connection_established
func connect_ws(url):
	var err = client.connect_to_url(url)
	return err
func connected(a):
	self.connected=true
	emit_signal("connection_established")
func _on_data():
	 on_data(client.get_peer(1).get_packet().get_string_from_utf8())
func on_data(string):
	json_resp=parse_json(string)
	emit_signal("on_json",json_resp)
	if json_resp["type"]=="message":
		emit_signal("on_message",json_resp)
func send_json(data):
	print(JSON.print(data))
	client.get_peer(1).put_packet(JSON.print(data).to_utf8())
func login(username,passwd):
	send_json({"type":"login","usrname":username,"msg":passwd,"uid":0,"uuid":"314e82b2-66af-4e4e-b454-9da0a72fed45"})
	yield(self,"on_json")
	if json_resp["type"]=="login":
		print(json_resp)
		self.uid=json_resp["uid"]
		return json_resp
func list_chat():
	send_json({"type":"chat_list_somebody_joined","uid":self.uid,"usrname":"","msg":""})
	return yield(self,"on_json")["msg"]
func send_message(chat,message):
	send_json({"type":"message","uid":chat,"msg":message})
	
