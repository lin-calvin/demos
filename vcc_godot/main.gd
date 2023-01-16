extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

var Chat=preload("res://ChatUI.tscn")
# Called when the node enters the scene tree for the first time.
func _ready():
	$Login.connect("login_success",self,"load_mainui")
func load_mainui():
	add_child(Chat.instance())
