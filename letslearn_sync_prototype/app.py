import flask
from flask import request
import json 
app=flask.Flask(__name__)
state={'notes':{}}
def reducer(state,action):
    if action['type']=="notes/add":
        state["notes"][action['content']['name']]=action['content']
    if action['type']=="nodes/del":
        del state['notes'][action['name']]
    return state

@app.route("/sync/<token>",methods=["POST"])
def sync(token):
    global state
    data=json.loads(request.data.decode())
    print(data)
    for i in data['data']:
        state=reducer(state,i)
    print(state)
    resp=flask.Response("")
    resp.headers["Access-Control-Request"]=""
    return resp
app.run()

