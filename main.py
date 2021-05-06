from fastapi import Depends, FastAPI, HTTPException, Query
import time
import sys
from function import wechat
from configparser import ConfigParser
from pydantic import BaseModel

configs = ConfigParser()
configs.read('config/config.ini')

allow_list = ['text', 'markdown']

class Item(BaseModel):
    message: str
    toUser: str = None
    method: str = "text"

app = FastAPI()

@app.get("/wechat/{push_type}/{method}")
async def corwechat(message: str, push_type:str, method: str):
    if method == 'markdown':
        message = message.replace(r'\n', '\n')
        message = message.replace('@', '#')
    else:
        method = 'text'

    if configs.has_section(push_type):
        corID = configs[push_type]['corID']
        corpsecret = configs[push_type]['corpsecret']
        agentid = configs[push_type]['agentid']
        toUser = configs[push_type]['toUser']
        access_token = configs[push_type]['access_token']
        over_time = configs[push_type]['over_time']

        access_token, over_time, response = wechat.wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, method, message)

        configs[push_type]['access_token'] = access_token
        configs[push_type]['over_time'] = over_time
        return response
    else:
        raise HTTPException(status_code = 404, detail="Invalid method ")

@app.post("/wechat/{push_type}/")
async def corwechat(push_type: str, item: Item):
    if item.method not in allow_list:
        raise HTTPException(status_code = 404, detail="Invalid method")
    if configs.has_section(push_type):
        corID = configs[push_type]['corID']
        corpsecret = configs[push_type]['corpsecret']
        agentid = configs[push_type]['agentid']
        if(item.toUser):
            toUser = configs[push_type]['toUser']
        else:
            toUser = configs[push_type]['toUser']
        access_token = configs[push_type]['access_token']
        over_time = configs[push_type]['over_time']

        access_token, over_time, response = wechat.wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, item.method, item.message)

        configs[push_type]['access_token'] = access_token
        configs[push_type]['over_time'] = over_time
    else:
        response = {"error": "invalid type"}
    return response

if __name__ == '__main__':
    import uvicorn
    if configs.has_section("common"):
        server_addr = configs['common']['server_addr']
        server_port = int(configs['common']['server_port'])
        uvicorn.run(app, host = server_addr, port = server_port)
    else:
        print("Please check config file")
