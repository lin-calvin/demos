extends Control

signal login_success
func _ready():
	pass # Replace with function body.
onready var client=$"../VccClient"
func do_connect():
	if  not client.connected:
		print(client.connect_ws($URL.text))
	yield(client,"connection_established")
	if yield(client.login($Username.text,$Password.text), "completed")["uid"]!=null:
		self.queue_free()
		emit_signal("login_success")
	else:
		$Label.visible=true
