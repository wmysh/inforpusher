from fastapi import FastAPI, HTTPException, Query, Form, Request
from loguru import logger
from function import wechat
from configparser import ConfigParser
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import markdown

configs = ConfigParser()
configs.read('config/config.ini')

templates = Jinja2Templates(directory="templates")

wechat_type_allow_list = ['text', 'markdown']

app = FastAPI()

def wechat_handle(type, message, toAgent, title, url):
    message = message.replace(r'\r', '\r')
    message = message.replace(r'\n', '\n')
    if not type:
        type = "text"
    if type not in wechat_type_allow_list:
        logger.error("Message type not allowed.")
        raise HTTPException(status_code = 404, detail="Message type not allowed.")
    if type == 'markdown':
            if not title:
                raise HTTPException(status_code = 404, detail="The title of markdown content not found.")
            message = message.replace('#', '%23')
            message = message.replace('&', '%26')
            message = message.replace('\r', r'\r')
            message = message.replace('\n', r'\n')
            url = configs['common']['base_url'] + '/md2html' + '?title='+ title + '&content=' + message
            type = 'textcard'
            message = "点击查看内容"
    elif type == 'text' and title:
        if url:
            type = 'textcard'
        else:
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
async def wechat_get(msg: str = Query(..., description = 'REQUIRED, The meessage you want to send.'), 
                        type: str = Query(None, description = "OPTIONAL AND DEFAULT TO TEXT, you can set the message tpye to text or markdown."),
                        toAgent: str = Query(None, description = "OPTIONAL AND DEFAULT SEND TO ALL, you can control who can receive this message."),
                        title: str = Query(None, description = "OPTIONAL AND DEFAULT TO None, the title of message. And if have both title and url, you will send a textcard."),
                        url: str = Query(None, description = "OPTIONAL AND DEFAULT TO None, the url of textcard. And if have both title and url, you will send a textcard.")
                        ):
    return wechat_handle(type, msg, toAgent, title, url)

@app.post("/wechat")
async def wechat_post(msg: str = Form(..., description = 'REQUIRED, The meessage you want to send.'), 
                        type: str = Form(None, description = "OPTIONAL AND DEFAULT TO TEXT, you can set the message tpye to text or markdown."),
                        toAgent: str = Form(None, description = "OPTIONAL AND DEFAULT SEND TO ALL, you can control who can receive this message."),
                        title: str = Form(None, description = "OPTIONAL AND DEFAULT TO None, the title of message. And if have both title and url, you will send a textcard."),
                        url: str = Form(None, description = "OPTIONAL AND DEFAULT TO None, the url of textcard. And if have both title and url, you will send a textcard.")
                        ):
    return wechat_handle(type, msg, toAgent, title, url)

@app.get("/md2html", response_class=HTMLResponse)
async def md2html(request: Request, 
                        content: str = Query(..., description = 'REQUIRED, The markdown content you want to show with html.'),
                        title: str = Query("Markdown to html", description = 'OPTIONAL, The title of the webpage.')
                        ):
    content = content.replace(r'\r', '\r')
    content = content.replace(r'\n', '\n')
    content = content.replace(r'%26', '&')
    html = markdown.markdown(content)
    return templates.TemplateResponse("item.html", {"request": request, "content": html, "title": title})

if __name__ == '__main__':
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
