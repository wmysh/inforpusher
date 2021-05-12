import json
import time
from loguru import logger
import requests

def get_access_token(corID, corpsecret):
    try:
        response = requests.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corID + '&corpsecret=' + corpsecret).text
    except:
        logger.error("Can't visit API, please Check gettoke API.")
        raise Exception("Can't visit API, please Check gettoke API.")
    else:
        if json.loads(response)["errcode"] != 0:
            logger.error(json.loads(response)["errmsg"])
            raise Exception(json.loads(response)["errmsg"])
        else:
            expires_in = json.loads(response)["expires_in"]
            over_time = str(time.time() + expires_in)
            access_token = json.loads(response)["access_token"]
            logger.info("Got new access_token.")
            return access_token, over_time

def wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, method, message, title, url):
    if method == "text" or  method == "markdown":
        data = {
            "touser": toUser,
            "msgtype": method,
            "agentid": agentid,
            method: {
                "content": message
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
    elif method == "textcard":
        data = {
            "touser": toUser,
            "msgtype": method,
            "agentid": agentid,
            method: {
                "title": title,
                "description": message,
                "url": url,
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }

    # if get_access_token overtime
    if time.time() > float(over_time):
        logger.info(f"{agentid}: Access_token overtime, will get new one.")
        access_token, over_time = get_access_token(corID, corpsecret)

    try:
        response = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token, json = data).text
        # retry if invalid access_token
    except:
        logger.error("Can't visit the send API, please Check gettoke API.")
        raise Exception("Can't visit the send API, please Check gettoke API.")
    else:
        if json.loads(response)["errcode"] == 40014:
            logger.error("Invalid access_token, will get new one.")
            access_token, over_time = get_access_token(corID, corpsecret)
            if access_token and over_time:
                response = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token, json = data).text
            else:
                raise Exception("Can't get correct access_token, please check API.")
        return access_token, over_time, response
