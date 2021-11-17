import base64
import json
import os
import random
import requests
import time

# С��ѧ�� �˺�����
USERNAME = os.getenv("XB_USERNAME_FMX")
PASSWORD = os.getenv("XB_PASSWORD_FMX")
# ��γ��
LOCATION = os.getenv("XB_LOCATION")
# λ�ã���ѡͨ���ӿڻ�ȡ
COORD = os.getenv("XB_COORD")
# �ʼ�����
# IS_EMAIL = os.getenv("XB_IS_EMAIL") #��Ҫ����ֱ�Ӹɵ�
# �����˺�
EMAIL = os.getenv("XB_EMAIL_FMX")
# ��ҵ΢��Ӧ��
WX_APP = os.getenv("XB_WXAPP")
# ��������
BASE_URL = "https://xiaobei.yinghuaonline.com/xiaobei-api/"

# header
HEADERS = {
    "user-agent": "iPhone10,3(iOS/14.4) Uninview(Uninview/1.0.0) Weex/0.26.0 1125x2436",
    "accept": "*/*",
    "accept-language": "zh-cn",
    "accept-encoding": "gzip, deflate, br"
}


def is_open():
    import platform
    # ֻ��winϵͳ�´�
    if platform.system() == 'Windows':
        reply = str(input("ѡ���Ƿ�ȥ��ȡ��γ�ȣ��˲������Ĭ�������[Y/N]��"))
        if reply == 'Y':
            import webbrowser
            webbrowser.open("https://api.xiaobaibk.com/api/map/")
        else:
            pass
    else:
        print("���������������ӻ�ȡ��γ�ȣ�https://api.xiaobaibk.com/api/map/")


# �жϻ����������Ƿ�Ϊ��
if USERNAME is None or PASSWORD is None:
    USERNAME = str(input("������С��ѧ���˺ţ�"))
    PASSWORD = str(input("������С��ѧ�����룺"))
    is_open()
    LOCATION = str(input("�뽫�������Ƶľ�γ��ճ�����˴���"))
    # COORD = str(input("�뽫�����ڵ������磺�й�-����ʡ-������-�ٶ�������"))
    EMAIL = input("���������˺�,�����򲻿���:")
    print("΢��֪ͨ,��������дKEY���̳̣�https://ghurl.github.io/?130")
    WX_APP = input("΢��֪ͨ��Կ,�����򲻿���:")
    PASSWORD = str(base64.b64encode(PASSWORD.encode()).decode())
else:
    PASSWORD = str(base64.b64encode(PASSWORD.encode()).decode())


def get_location():
    lc = LOCATION.split(',')
    location = lc[1] + ',' + lc[0]
    url = "https://api.xiaobaibk.com/api/location/?location=" + location
    result = requests.get(url).text
    data = json.loads(result)
    if data['status'] == 0:
        province = data['result']['addressComponent']['province']
        city = data['result']['addressComponent']['city']
        district = data['result']['addressComponent']['district']
        return '�й�-' + province + '-' + city + '-' + district
    else:
        print("λ�û�ȡʧ��,������ֹ")
        os._exit(0)


def get_param(coord):
    # �������Ϊ35.7~36.7
    temperature = str(random.randint(357, 367) / 10)
    # 107.807008,26.245838
    rand = random.randint(1111, 9999)
    # ����
    location_x = LOCATION.split(',')[0].split('.')[0] + '.' + LOCATION.split(',')[0].split('.')[1][0:2] + str(rand)
    # γ��
    location_y = LOCATION.split(',')[1].split('.')[0] + '.' + LOCATION.split(',')[1].split('.')[1][0:2] + str(rand)
    location = location_x + ',' + location_y
    return {
        "temperature": temperature,
        "coordinates": coord,
        "location": location,
        "healthState": "1",
        "dangerousRegion": "2",
        "dangerousRegionRemark": "",
        "contactSituation": "2",
        "goOut": "1",
        "goOutRemark": "",
        "remark": "��",
        "familySituation": "1"
    }


def send_mail(context):
    url = "https://api.xiaobaibk.com/api/mail/"
    js = {'mailto': EMAIL, 'content': context}
    # {"code":200,"msg":"\u606d\u559c\u60a8\u53d1\u9001\u6210\u529f\u4e86"}
    result = requests.post(url, js).text
    type = json.loads(result)['code']
    if type == 200:
        print("֪ͨ���ͳɹ���")
    else:
        print("֪ͨ����ʧ�ܣ�ԭ��" + json.loads(result)['msg'])


def wxapp_notify(content):
    app_params = WX_APP.split(',')
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'corpid': app_params[0],
        'corpsecret': app_params[1],
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(payload), timeout=15).json()
    accesstoken = response["access_token"]
    content = "�������[" + content + "]\n��λ�ã�[" + COORD + "]\n�����ڣ�[" + time.strftime("%Y-%m-%d") + "]"
    html = content.replace("\n", "<br/>")
    options = {
        'msgtype': 'mpnews',
        'mpnews': {
            'articles': [
                {
                    'title': 'С����֪ͨ',
                    'thumb_media_id': f'{app_params[4]}',
                    'author': 'С��',
                    'content_source_url': '',
                    'content': f'{html}',
                    'digest': f'{content}'
                }
            ]
        }
    }

    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={accesstoken}"
    data = {
        'touser': f'{app_params[2]}',
        'agentid': f'{app_params[3]}',
        'safe': '0'
    }
    data.update(options)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()

    if response['errcode'] == 0:
        print('��ҵ΢��Ӧ��֪ͨ�ɹ���')
    else:
        print('��ҵ΢��Ӧ��֪ͨʧ�ܣ�')


if __name__ == '__main__':
    # Url
    # ������֤
    captcha = BASE_URL + 'captchaImage'
    # captcha = 'https://xiaobei.yinghuaonline.com/xiaobei-api/captchaImage'
    # https://xiaobei.yinghuaonline.com/xiaobei-api/captchaImage
    # ��¼
    login = BASE_URL + 'login'
    # ��
    health = BASE_URL + 'student/health'

    # post method return 500 , So use the get method
    # data:   {"msg":"�����ɹ�","img":"xxxxxx","code":200,"showCode":"NM6B","uuid":"4f72776b789b44d796722037ba7a1ff0"}
    response = requests.get(url=captcha, headers=HEADERS).text
    # ȡ��uuid��showCode
    uuid = json.loads(response)['uuid']
    showCode = json.loads(response)['showCode']

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "code": showCode,
        "uuid": uuid
    }

    # ��¼����
    # success return {"msg":"�����ɹ�","code":200,"token":"eyJhb....."}
    # error return {"msg":"�û�������/�������","code":500}
    res = requests.post(url=login, headers=HEADERS, json=data).text
    code = json.loads(res)['code']
    msg = json.loads(res)['msg']


    if code != 200:
        print("Sorry! Login failed! Error��" + msg)
        # �����ʼ�
        if EMAIL != '':
            send_mail("��¼ʧ�ܣ�ʧ��ԭ��" + msg)
        if WX_APP != '':
            wxapp_notify("��¼ʧ�ܣ�ʧ��ԭ��" + msg)
    else:
        print("��¼�ɹ���")

        # HEADERS.update({'authorization', token})
        # ��������
        HEADERS['authorization'] = json.loads(res)['token']

        # ��ȡλ��
        if COORD is None or COORD == '':
            COORD = get_location()
        else:
            pass

        health_param = None

        print(COORD)
        if LOCATION is not None and COORD is not None:
            health_param = get_param(COORD)
        else:
            print("��Ҫ����Ϊ�գ�")

        respond = requests.post(url=health, headers=HEADERS, json=health_param).text
        # error return {'msg': None, 'code': 500}
        # succeed return {'msg': '�����ɹ�', 'code': 200}
        status = json.loads(respond)['code']
        if status == 200:
            print("��ϲ���򿨳ɹ�����")
            if EMAIL != '':
                send_mail("�򿨳ɹ����9�5")
            if WX_APP != '':
                wxapp_notify("�򿨳ɹ����9�5")
        else:
            print("Error��" + json.loads(respond)['msg'])
            if EMAIL != 'yes':
                send_mail("�0�1��Ǹ��ʧ���ˣ�ԭ��δ֪���������ֶ��򿨣�лл")
            if WX_APP != '':
                wxapp_notify("�0�1��Ǹ��ʧ���ˣ�ԭ��δ֪���������ֶ��򿨣�лл")
