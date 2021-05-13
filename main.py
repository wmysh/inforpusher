from fastapi import FastAPI, HTTPException
from loguru import logger
from function import wechat
from configparser import ConfigParser
from pydantic import BaseModel

configs = ConfigParser()
configs.read('config/config.ini')

wechat_type_allow_list = ['text', 'markdown']

class Item(BaseModel):
    msg: str
    toAgent: str = None
    type: str = "text"
    title: str = None
    url: str = None

app = FastAPI()

def wechat_handle(type, message, toAgent, title, url):
    if type not in wechat_type_allow_list:
        logger.error("Message type not allowed.")
        raise HTTPException(status_code = 404, detail="Message type not allowed.")
    if type == 'markdown':
        message = message.replace(r'\n', '\n')
        message = message.replace('@', '#')
    if title and url and type == 'text':
        type = 'textcard'
    if title and not url:
        message = '[' + title + ']\n' + message
    if toAgent:
        agent = 'wechat' + '-' + toAgent
    else:
        agent = 'wechat'
    if configs.has_section(agent):
        try:
            corID = configs[agent]['corID']
            corpsecret = configs[agent]['corpsecret']
            agentid = configs[agent]['agentid']
            toUser = configs[agent]['toUser']
        except:
            raise HTTPException(status_code = 404, detail="Please check server config")
        try:
            access_token = configs[agent]['access_token']
            over_time = configs[agent]['over_time']
        except:
            logger.info(f"Agent {agent}'s access_token not found, will set to default.")
            access_token = 0
            over_time = 0
        try:
            access_token, over_time, response = wechat.wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, type, message, title, url)
            configs[agent]['access_token'] = access_token
            configs[agent]['over_time'] = over_time
        except:
            logger.error("Wechat Send fail, please check API.")
            raise HTTPException(status_code = 500, detail="Wechat Send fail, please check API.")
        else:
            return response
    else:
        raise HTTPException(status_code = 404, detail="Unaviable agent, please add to config.")

@app.get("/wechat")
async def wechat_get(msg: str, type: str = 'text', toAgent: str = None, title: str = None, url: str = None):
    return wechat_handle(type, msg, toAgent, title, url)

@app.post("/wechat")
async def wechat_post(item: Item):
    return wechat_handle(item.type, item.msg, item.toAgent, item.title, item.url)

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
