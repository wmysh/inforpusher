import json
import time
import requests

def get_access_token(corID, corpsecret):
    response = requests.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corID + '&corpsecret=' + corpsecret).text
    if response == '':
        print("please Check gettoke API")
        return None, None
    elif json.loads(response)["errcode"] != 0:
        print(json.loads(response)["errmsg"])
        return None, None
    else:
        expires_in = json.loads(response)["expires_in"]
        over_time = str(time.time() + expires_in)
        access_token = json.loads(response)["access_token"]
        return access_token, over_time

def wechat_msg_send(corID, corpsecret, agentid, toUser, access_token, over_time, method, message):
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

    # if get_access_token overtime
    if time.time() > float(over_time):
        print('timeover')
        access_token, over_time = get_access_token(corID, corpsecret)

    if access_token and over_time:
        response = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token, json = data).text
        # retry if invalid access_token
        if json.loads(response)["errcode"] == 40014:
            print('invalid access_token')
            access_token, over_time = get_access_token(corID, corpsecret)
            if access_token and over_time:
                response = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token, json = data).text
            else:
                print("error, Please check item")
        return access_token, over_time, response
    else:
        print("error")
        return {"errorcode":500}