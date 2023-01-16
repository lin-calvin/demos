extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

onready var client=$"../VccClient"
onready var chatbox=$HBoxContainer/VBoxContainer/TextEdit
var message="{usrname}:\n    {msg}\n"
var chats=[]
var current_chat=null
# Called when the node enters the scene tree for the first time.
func _ready():
	print(client)
	client.connect("on_message",self,"on_message")
	self.chats=yield(client.list_chat(),"completed")
	self.current_chat=self.chats[0]
	for i in self.chats:
		$HBoxContainer/ItemList.add_item(i[1])
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
func on_message(msg):
	if msg["uid"]==self.current_chat[0]:
		var text=message.format(msg)
		chatbox.text+=text
		chatbox.scroll_vertical=chatbox.get_line_count() 


func change_chat(index):
	if self.current_chat!=self.chats[index]:
		print("change!")
		self.current_chat=self.chats[index]
		chatbox.text=""


func send_message(text):
	self.client.send_message(self.current_chat[0],text)
	$HBoxContainer/VBoxContainer/LineEdit.text=""
