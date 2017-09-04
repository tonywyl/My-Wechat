from django.shortcuts import render,HttpResponse,redirect
from bs4 import  BeautifulSoup
import requests

import time
import re
import json
# Create your views here.
def login(req):
    """
    生成二维码
    :param req:
    :return:
    """
    if req.method=='GET':

        uuid_time=int(time.time()*1000)

        base_uuid_url="https://login.wx2.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={time_c}".format(time_c=uuid_time)

        r1=requests.get(base_uuid_url)

        result=re.findall('= "(.*)";',r1.text)
        print(r1.text,'00-0-0-0---0')
        uuid=result[0]
        print(r1.text,result,'0000000')
        req.session['UUID']=uuid
        req.session['UUID_TIME']=uuid_time
        
        return render(req,'login.html',{'uuid':uuid})


def check_login(req):
    
    """
    如果有人一扫，就会有请求,如果请求一直在刷新则tip=1,
    :param req:
    :return:
    https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=AZBLtUzABg==&tip=0&r=-735610385&_=1503974138377

    """
    response={'code':408,'data':None}


    ctime=int(time.time()*1000)
    
    tip=0
    print('uuid',req.session['UUID'],'----')
    base_login_url="https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip={tip}&r=-753225878&_={time_c}".format(uuid=req.session['UUID'],time_c=ctime,tip=tip)
    # base_login_url = "https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=-735595472&_={1}"

    login_url=base_login_url.format(req.session['UUID'],ctime)

    r1=requests.get(login_url)


    # print(r1.text)
    if 'window.code=408' in r1.text:
        #无人扫码
        print('408')
        response['code']=408

    elif 'window.code=201' in r1.text:
        #扫码，返回头像
        print('201')
        
        response['code']=201
        response['data']=re.findall("window.userAvatar = '(.*)';",r1.text)[0]

    elif 'window.code=200' in r1.text:
        #扫码，并确认登录
        response['code'] = 200
        print('200')
        req.session['LOGIN_COOKIE']=r1.cookies.get_dict()
        base_redirect_url=re.findall('redirect_uri="(.*)";',r1.text)[0]

        redirect_url=base_redirect_url+'&fun=new&version=v2'

        # print(redirect_url,'-=-=-=-=-')
        #获取凭证证   这一次是获取凭证  通过查看浏览器的网络 ，<error>......</error> 这个关键的标签
        r2=requests.get(redirect_url)
        # print(r2.text,'-------')

        soup=BeautifulSoup(r2.text,features='lxml')

        ticket_dict = {}
        ticket_dict['Skey']=soup.find(name='skey').text
        ticket_dict['Sid']=soup.find(name='wxsid').text
        ticket_dict['Uin']=soup.find(name='wxuin').text
        ticket_dict['ticket']=soup.find(name='pass_ticket').text
        post_data={
            'BaseRequest':{
                'DeviceID':"e384757757885382",
                'Sid':ticket_dict['Sid'],
                'Uin':ticket_dict['Uin'],
                'Skey':ticket_dict['Skey'],
                'ticket':ticket_dict['ticket'],
            }
        }

        print('-------------------------------------------------')
        # print(post_data,'========')
        req.session['TICKED_DICT']=ticket_dict
        req.session['TICKED_COOKIE']=r2.cookies.get_dict()

        """
        BaseRequest:
            {Uin: "1739220102", Sid: "xSgnIyDDB8vzrRIr", Skey: "@crypt_4812c541_b97d890e2c45c8d64fff0c9c1fe4fe8d",…}
            DeviceID:
            "e764666339646217"
            Sid:
            "xSgnIyDDB8vzrRIr"
            Skey:
            "@crypt_4812c541_b97d890e2c45c8d64fff0c9c1fe4fe8d"
            Uin:
            "1739220102"
        """
        #初始化URL获取最近联系人，及公众号
        get_firends_url="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-762083778&lang=zh_CN&pass_ticket=%s"%(ticket_dict['ticket'])

        get_firends_post=requests.post(get_firends_url,json=post_data)

        get_firends_post.encoding='utf-8'
        # print(get_firends_post.text)

        get_firends_list=json.loads(get_firends_post.text)#因为这里拿到的text是字符串，所以 需要loads 序列成字典。
        
        # print(get_firends_list)

        req.session['INIT_DICT']=get_firends_list

        # print(req.session['INIT_DICT'],'-=-=-=-=-=-=-=-=-=-=')

        response['code']=200

        #获取最近联系信息，公众号#  Sid ,Uin  Skey  都在<error>......</error>,Device 用默认的。

        #syncKey 重要∆ #浏览器里的检查----> Preview

    return HttpResponse(json.dumps(response))


def index(req):
    """
    显示最近联系人，最近公共号信息,index 页面
    :param req:
    :return:
    """
    """
    https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-759225233&lang=zh_CN&pass_ticket=f9xFGzFnNOu1j9dT4ku6a3TXkAV8QWNe9FqhhC5DK4dJSNkzzR%252FrpNtZCYSJp3%252BD
    
    """
    """
     BaseRequest:
        {Uin: "1739220102", Sid: "aCg+e7pNbLUyVLL4", Skey: "@crypt_4812c541_b103fad26c47df6576be5b0b26c6a996",…}
        DeviceID:
        "e220272036798391"
        Sid:
        "aCg+e7pNbLUyVLL4"
        Skey:
        "@crypt_4812c541_b103fad26c47df6576be5b0b26c6a996"
        Uin:
        "1739220102"
"""
    img_url='https://wx.qq.com'+req.session['INIT_DICT']['User']['HeadImgUrl']

    img_result=requests.get(img_url,headers={'Referer':'https://wx2.qq.com/?&lang=zh_CN'})
    print(img_result.content,'======')
    print(img_result.text,'======')

    return render(req,'index.html')



def avatar(req):
    """
    获取 自己头像
    :param req:
    :return:
    """
    prev=req.GET.get('prev')#获取图像的前缀  #/cgi-bin/mmwebwx-bin/webwxgeticon?seq=602427528
    username=req.GET.get('username')
    skey=req.GET.get('skey')

    img_url='https://wx.qq.com{prev}&username={username}&skey={skey}'.format(prev=prev,username=username,skey=skey)



    #refer获取头像不成功，还需要cookie才能获取到
    cookies={}
    cookies.update(req.session['LOGIN_COOKIE'])
    cookies.update(req.session['TICKED_COOKIE'])
    # print(img_url)
    res=requests.get(img_url,cookies=cookies,headers={'Content-Type':'image/jpeg'})
    
    

    
    return HttpResponse(res.content)




def sendmsg(req):
    """
    :param req:
    :return:
    """

    """
        https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?pass_ticket=QvsMUtHJG5x7WStYIIGwH6H9AGGDR6YYe0r26qtK2XRTXXO5tvXkeoY%252FZg6xz8Za
    """

    """
    BaseRequest:
        {Uin: 1739220102, Sid: "7ojLQ4Fi8L/ahpBW", Skey: "@crypt_4812c541_1f996e9023e0f8681ed0d6a9077e2ece",…}
        DeviceID:
        "e174105737115933"
        Sid:
        "7ojLQ4Fi8L/ahpBW"
        Skey:
        "@crypt_4812c541_1f996e9023e0f8681ed0d6a9077e2ece"
        Uin:
        1739220102
    Msg:
        {Type: 1, Content: "afdsafds",…}
        ClientMsgId:
        "15040530942420974"
        Content:
        "afdsafds"
        FromUserName:
        "@b9f576621c2182df7c12bd00275c2b0bff16981a6f7b7d9ec1d6e0ccae77479c"
        LocalID:
        "15040530942420974"
        ToUserName:
        "@abac16a1f3076ac2b7ed02992be0d75c"
        Type:1
    Scene:0
    """
    cont=req.POST.get('sendmsg')
    to_user=req.POST.get('to_user')
    csrf_token=req.POST.get('csrfmiddlewaretoken')
    # print(cont,'-------',to_user,'------',csrf_token)

    current_user = req.session['INIT_DICT']['User']['UserName']
    ctime = int(time.time())
    post_data={
        "BaseRequest":{
            'Uin':req.session['TICKED_DICT']['Uin'],
            'DeviceID':'e174105737115933',
            'Sid':req.session['TICKED_DICT']['Sid'],
            'Skey':req.session['TICKED_DICT']['Skey'],
        },
        'Msg':{
        'ClientMsgId':ctime,
        'Content':cont,
        'FromUserName':current_user,
        'LocalID':ctime,
        'ToUserName':to_user,
        'Type':1
        },
        'Scene':0
    }
    
    # print(current_user,'current_user','---------','Uin',req.session['TICKED_DICT']['Uin'],'-----','https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket=%s'%(req.session['TICKED_DICT']['ticket']))
    
    sendmsg_url=requests.post('https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket=%s'%(req.session['TICKED_DICT']['ticket']),data=json.dumps(post_data,ensure_ascii=False).encode('utf-8'),headers={'Content-Type':'application/json'})#json 的contenttype 就等于 application/json;charset=UTF-8    data等于 其它
    # 因为requests内部做一个事情将数据都JSON.DUMP成字符串，字符串不能直接发送，requests会将这个字符串JSON成bytes 然后再发，并且字符编码方式为latin1 (拉丁1) ,所以也就解析不了中文，所以这里ensure_ascii=False,并且编码方式成utf-8
    print(sendmsg_url.status_code)

    return HttpResponse('hahahaha')


def contact_list(req):
    return render(req,'contact_list.html')

def send_msg(req):
    """
    发送消息
    :param req:
    :return:
    """
    current_user='@abac16a1f3076ac2b7ed02992be0d75c'
    to=req.POST.get('to')
    msg=req.POST.get('msg')
    #
def getmsg(req):
    """
    recv message
    :param req:
    :return:
    """
    """
    https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=emFoJcyxfzlggP6A&skey=@crypt_4812c541_baad7e32e3658cc66e2bca39afb1bb13&lang=zh_CN
    """


    """
    post_data:
    BaseRequest:
        {
        DeviceID:"e898925842177650"
        Sid:"emFoJcyxfzlggP6A"
        Skey:"@crypt_4812c541_baad7e32e3658cc66e2bca39afb1bb13"
        Uin:1739220102}
        SyncKey:{
        Count:9
        List:[0:{Key: 1, Val: 654905689}
        ,1:{Key: 2, Val: 654906250}
        ,2:{Key: 3, Val: 654906083}
        ,3:{Key: 11, Val: 654906122}
        ,4:{Key: 13, Val: 654880019}
        ,5:{Key: 201, Val: 1504091023}
        ,6:{Key: 203, Val: 1504083373}
        ,7:{Key: 1000, Val: 1504088282}
        ,8:{Key: 1001, Val: 1504088313}]
        }
        rr:-85252837
    
    get_data:
        r:1504091982039
        skey:@crypt_4812c541_baad7e32e3658cc66e2bca39afb1bb13
        sid:emFoJcyxfzlggP6A
        uin:1739220102
        deviceid:e712772708331341
        synckey:1_654905689|2_654906257|3_654906083|11_654906122|13_654880019|201_1504091956|203_1504083373|1000_1504088282|1001_1504088313
        _:1504091638166
    """
    ctime=int(time.time())
    print('----------------------------------------------------------------------------------------------------------------------------')
    # print(req.session['INIT_DICT']['SyncKey'])
    print('------------------',req.session['TICKED_DICT'],'------------------')
    # block_url="https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r={ctime}&skey={skey}&uin={uin}&deviceid={deviceid}&synckey={synckey}&_={ctime2}".format(ctime=ctime,skey=req.session['TICKED_DICT']['Skey'],uin=req.session['TICKED_DICT']['Uin'],synckey=req.session['INIT_DICT']['SyncKey'],ctime2=ctime)


    syncKey_dict=req.session['INIT_DICT']['SyncKey']
    print('-----------------------------',req.session['INIT_DICT']['SyncKey'])
    #{'List': [{'Val': 654905689, 'Key': 1}, {'Val': 654906279, 'Key': 2}, {'Val': 654906083, 'Key': 3}, {'Val': 1504088282, 'Key': 1000}], 'Count': 4}

    
    block_url="https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"
    blocking_url=requests.get(
        url=block_url,
        params={
        'r':ctime,
        'skey':req.session['TICKED_DICT']['Skey'],
        'sid':req.session['TICKED_DICT']['Sid'],
        'uin':req.session['TICKED_DICT']['Uin'],
        'deviceid':'e395767210919364',
        'synckey':req.session['INIT_DICT']['SyncKey'],
        '_':ctime,
    })
    print('==================',blocking_url.text,'=-=-=-=--=')
    
    get_dynamic='https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync'
    
    if '{retcode:"0",selector:"0"}'  in blocking_url.text:
        return HttpResponse('....')

    post_data = {
        "BaseRequest": {
            'Uin': req.session['TICKED_DICT']['Uin'],
            'DeviceID': 'e174105737115933',
            'Sid': req.session['TICKED_DICT']['Sid'],
            'Skey': req.session['TICKED_DICT']['Skey'],
        },
        'SyncKey':req.session['INIT_DICT']['SyncKey']
    }
    
    r2=requests.post(url=get_dynamic,json=post_data)

    r2.encoding='utf-8'
    msg_dict=json.loads(r2.text)
    for msg in msg_dict['AddMsgList']:
        print('new message',msg['Content'])

    init_dict=req.session['INIT_DICT']

    init_dict['SyncKey']=msg_dict['SyncKey']
    req.session['INIT_DICT']=init_dict


    req.session['INIT_DICT']['SyncKey']

    
    return HttpResponse('lllll')

def get_msg(req):
    """
    长轮询获取消息
    :param req:
    :return:
    """
    #一#检测消息到来
    #接收消息：
    """
    阻塞URL:https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1504091653034&skey=%40crypt_4812c541_baad7e32e3658cc66e2bca39afb1bb13&sid=emFoJcyxfzlggP6A&uin=1739220102&deviceid=e395767210919364&synckey=1_654905689%7C2_654906254%7C3_654906083%7C11_654906122%7C13_654880019%7C201_1504091652%7C203_1504083373%7C1000_1504088282%7C1001_1504088313&_=1504091638151
    如果有消息则用下面请求：
    https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1504059707063&skey=%40crypt_4812c541_3223ac18e60b6a11482292139e0d092f&sid=mTZ9cmslqre%2B4bnn&uin=1739220102&deviceid=e336521333013526&synckey=1_654905689%7C2_654906047%7C3_654906025%7C11_654905791%7C13_654880019%7C201_1504059631%7C1000_1504054982%7C1001_1504055013%7C1002_1503481241&_=1504058316943
    """
    ctime=int(time.time()*1000)
    ticket=req.session['TICKED_DICT']
    check_msg_url="https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"

    syncKey_dict=req.session['INIT_DICT']['SyncKey']

    synckey_list=[]
    for item in syncKey_dict['LIST']:
        tmp='%s_%s'%(item['Key'],item['Val'])
        synckey_list.append(tmp)
    synckey="|".join(synckey_list)

    r1=requests.get(
        url=check_msg_url,
        params={
            'r':ctime,
            'uin':req.session['TICKED_DICT']['Uin'],
            'deviceid':'e174105737115933',
            'sid':req.session['TICKED_DICT']['Sid'],
            'skey':req.session['TICKED_DICT']['Skey'],
            '_':ctime,
            'synckey':synckey

        },
    )

    #判断window.syncheck={retcode:'0',selector:'0'}
    #判断window.syncheck={retcode:'0',selector:'2'}
    if '{retcode:"0",selector:"0"}' in r1.text:
        return HttpResponse('....')
    #二 ，如果有消息，则获取
    # 如果有消息则执行Post请求
    """
    https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=mTZ9cmslqre+4bnn&skey=@crypt_4812c541_3223ac18e60b6a11482292139e0d092f&lang=zh_CN&pass_ticket=2ufdD9bCNlThgrtU4zZlhc1rAhZbArp6AvYlsH0SlK%252BYatx5wriR7FLrW9mbIvpz
    Request Method:POST


    """

    base_get_msg_url="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=mTZ9cmslqre+4bnn&skey=@crypt_4812c541_3223ac18e60b6a11482292139e0d092f&lang=zh_CN&pass_ticket=2ufdD9bCNlThgrtU4zZlhc1rAhZbArp6AvYlsH0SlK%252BYatx5wriR7FLrW9mbIvpz"

    post_data={
        "BaseRequest": {
            'Uin': req.session['TICKED_DICT']['Uin'],
            'DeviceID': 'e174105737115933',
            'Sid': req.session['TICKED_DICT']['Sid'],
            'Skey': req.session['TICKED_DICT']['Skey'],
        },
        'SyncKey':req.session["INIT_DICT"]['SyncKey'],
    }

    r2=requests.post(url=base_get_msg_url,json=post_data)

    #r2接收到的消息：消息里有skynckey,每次接收后都 会有新的skynkey，第一次初始化有个skynckey,这一次的synckey会更新初始化的synckey
    r2.encoding='utf-8'
    msg_dict=json.loads(r2.text)
    for msg in msg_dict['AddMsgList']:
        print(msg['Content'])
    print(msg_dict['SyncKey']) #取到消息里synckey 这个key要更新session 的synckey

    #因为session是从数据库里拿的，然后读到内存，如果现在改变这个值并没有修改到数据库里的值,
    #所以，不能直接赋给 req.session['INIT_DICT']['SyncKey']=msg['Content'],除此外，
    #还需要cookie 里设置。


    init_dict=req.session['INIT_DICT']

    req.session['INIT_DICT']['SyncKey']



    #无消息。

    return  HttpResponse('.....')

















