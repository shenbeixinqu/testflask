import json
import urllib.request

class Wechat:
    def __init__(self):
        # 企业ID
        self.CORP_ID = 'wwe6a967e2bfd97adf'
        # 自建应用secret
        self.CORP_SECRET = "OlUqc-u55dBWZp35iMB0c3SBybnCjgRDko8YkxMIDLk"
        self.APP_ID = '1000015'  # 应用ID，在后台应用中获取
        self.BASEURL = 'https://qyapi.weixin.qq.com/cgi-bin/'
        self.TOKEN_URL = 'gettoken?corpid={0}&corpsecret={1}'.format(self.CORP_ID, self.CORP_SECRET)

    # 获取认证 token
    def Get_Token(self):
        try:
            response = urllib.request.urlopen('{0}{1}'.format(self.BASEURL, self.TOKEN_URL))
            access_token = json.loads(response.read().decode('utf-8'))['access_token']
            with open('token', 'w') as f:
                f.write(access_token)
        except KeyError:
            raise KeyError
        return access_token

        # 本地 token

    def Local_Token(self):
        try:
            with open('token', 'r') as f:
                token = f.readline().strip()
                if token == '':
                    token = self.Get_Token()
                    return token
                else:
                    return token
        except IOError:
            token = self.Get_Token()
            return token

    #获取报警人员名单
    def Get_user(self,dep_id,fchild):
        token = self.Local_Token()
        send_url = '{0}user/list?access_token={1}&department_id={2}&fetch_child{3}'.format(self.BASEURL,token,dep_id,fchild,)
        respone = urllib.request.urlopen(url=send_url).read()
        stat = json.loads(respone)['userlist']
        user = ''
        for k in stat:
            user += '{0} '.format(k['mobile'])
        mobile = ",".join(user.split())
        with open("user.txt",'w') as f:
            f.write(mobile)

    # 发送报警消息
    def Send_Message(self,content):
        self.content={
            "touser":"Stephanie",  #成员,@all及所有人
            "msgtype": 'text',     # 消息类型
            "agentid": self.APP_ID,# 企业id
            "text": {
                "content": content  # 报警内容
            }
        }
        token = self.Local_Token()
        # 构建告警信息,必须是json格式
        msg = json.dumps(self.content)
        send_url = '{0}message/send?access_token={1}'.format(self.BASEURL,token)
        respone = urllib.request.urlopen(url=send_url, data=msg.encode("utf-8")).read()
        stat = json.loads(respone.decode())['errcode']
        if stat == 0:
            print('发送成功')
        else:
            token = self.Get_Token()
            send_url = '{0}message/send?access_token={1}'.format(self.BASEURL, token)
            respone = urllib.request.urlopen(url=send_url, data=msg).read().decode('utf-8')
            return respone


if __name__ == '__main__':
    msg = '123'
    wechat = Wechat()
    wechat.Send_Message(msg)