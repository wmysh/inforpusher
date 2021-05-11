from fastapi import Depends, FastAPI, HTTPException, Query
import time
import sys
from loguru import logger
from function import wechat
from configparser import ConfigParser
from pydantic import BaseModel

configs = ConfigParser()
configs.read('config/config.ini')

allow_list = ['text', 'markdown']

class Item(BaseModel):
    message: str
    toUser: str = "@all"
    method: str = "text"
    title: str = None
    url: str = None

app = FastAPI()

@app.get("/wechat/{push_type}/{method}")
async def corwechat(message: str, push_type: str, method: str, title: str = None, url: str = None):
    if method == 'markdown':
        message = message.replace(r'\n', '\n')
        message = message.replace('@', '#')
    else:
        method = 'text'
    if title and url and method == 'text':
        method = 'textcard'
    if title and not url:
        message = '[' + title + ']\n' + message

    if configs.has_section(push_type):
        try:
            corID = configs[push_type]['corID']
            corpsecret = configs[push_type]['corpsecret']
            agentid = configs[push_type]['agentid']
            toUser = configs[push_type]['toUser']
        except:
            raise HTTPException(status_code = 404, detail="Please check server config")
        try:
            access_token = configs[push_type]['access_token']
            over_time = configs[push_type]['over_time']
        except:
            logger.info("Access_token not found, will set to default.")
            access_token = 0
            over_time = 0
        try:
            access_token, over_time, response = wechat.wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, method, message, title, url)
            configs[push_type]['access_token'] = access_token
            configs[push_type]['over_time'] = over_time
        except:
            logger.error("Wechat Send fail, please check API.")
            raise HTTPException(status_code = 500, detail="Wechat Send fail, please check API.")
        else:
            return response
    else:
        raise HTTPException(status_code = 404, detail="Invalid method")

@app.post("/wechat/{push_type}/")
async def corwechat(push_type: str, item: Item):
    if item.method not in allow_list:
        raise HTTPException(status_code = 404, detail="Invalid method")
    if item.method == 'markdown':
        item.message = item.message.replace(r'\n', '\n')
        item.message = item.message.replace('@', '#')
    if item.title and item.url and item.method == 'text':
        item.method = 'textcard'
    if item.title and not item.url:
        item.message = '[' + item.title + ']\n' + item.message

    if configs.has_section(push_type):
        try:
            corID = configs[push_type]['corID']
            corpsecret = configs[push_type]['corpsecret']
            agentid = configs[push_type]['agentid']
            if(item.toUser):
                toUser = item.toUser
            else:
                toUser = configs[push_type]['toUser']
        except:
            raise HTTPException(status_code = 404, detail="Please check server config")
        try:
            access_token = configs[push_type]['access_token']
            over_time = configs[push_type]['over_time']
        except:
            logger.info("Access_token not found, will set to default.")
            access_token = 0
            over_time = 0
        try:
            access_token, over_time, response = wechat.wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, item.method, item.message, item.title, item.url)
            configs[push_type]['access_token'] = access_token
            configs[push_type]['over_time'] = over_time
        except:
            logger.error("Wechat Send fail, please check API.")
            raise HTTPException(status_code = 500, detail="Wechat Send fail, please check API.")
        else:
            return response
    else:
        raise HTTPException(status_code = 404, detail="Invalid method")

if __name__ == '__main__':
    import uvicorn
    try:
        server_addr = configs['common']['server_addr']
    except:
        logger.info('Use default address config')
        server_addr = "127.0.0.1"
    try:
        server_port = int(configs['common']['server_port'])
    except:
        logger.info('Use default port config')
        server_port = 8234
    uvicorn.run(app, host = server_addr, port = server_port)
