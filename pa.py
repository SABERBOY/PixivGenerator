import sys
import requests
import re
import os
import datetime
import json

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'referer': 'https://www.pixiv.net/ranking.php?mode=daily&content=illust',
}

path = './pixiv/'
repeat = 1
repeat_user_name = 1


def getSinglePic(url,picPath):
    global repeat
    global repeat_user_name
    response = requests.get(url, headers=headers)
    if re.search('"xRestrict":(.+?),"sl"', response.text).group() != '"xRestrict":0,"sl"':
        return False
    # 提取图片名称
    name = re.search('"illustTitle":"(.+?)"', response.text)
    name = name.group(1)
    illust_id = re.search('"illustId":"(.+?)"', response.text)
    illust_id = illust_id.group(1)
    user_name = re.search('"userName":"(.+?)"', response.text)
    user_name = user_name.group(1)
    if re.search('[\\\ \/ \* \? \" \: \< \> \|]', name) != None:
        name = re.sub('[\\\ \/ \* \? \" \: \< \> \|]', str(repeat), name)
        repeat += 1
    if re.search('[\\\ \/ \* \? \" \: \< \> \|]', user_name) != None:
        user_name = re.sub('[\\\ \/ \* \? \" \: \< \> \|]', str(repeat_user_name), user_name)
        repeat_user_name += 1
    # 提取图片原图地址
    picture = re.search('"original":"(.+?)"},"tags"', response.text)
    pic = requests.get(picture.group(1), headers=headers)
    f = open(picPath + '%s_%s-by-%s.%s' % (illust_id, name, user_name, picture.group(1)[-3:]), 'wb')
    f.write(pic.content)
    f.close()
    return True


def generateJson():
    pixivPath = './pixiv/'
    pixivJsonPath = './pixiv/url.json'
    path = [os.path.join(dp, f) for dp, dn, fs in os.walk(pixivPath) for f in fs if
                os.path.splitext(f)[1] in ['.jpg', '.png']]
    pixiv_json={"pixiv":path}
    jj=json.dumps(pixiv_json)
    f = open(pixivJsonPath, 'wb')
    f.write(jj.encode())
    f.close()

def getAllPicUrl():
    count = 1
    dataTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    for n in range(1, 2):
        url = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%d&format=json' % n
        response = requests.get(url, headers=headers)
        illust_id = re.findall('"illust_id":(\d+?),', response.text)
        picPath=path+dataTime+'/'+str(n)
        if not os.path.exists(picPath):
            os.makedirs(picPath)
        picUrl = ['https://www.pixiv.net/artworks/' + i for i in illust_id]
        for url in picUrl:
            print('Downloading the picture %d ' % count, end='   ')
            print('OK' if getSinglePic(url,picPath) else "FAILED", end='\n')
            count += 1
    os.system("ls -al")
    generateJson()
    return None

getAllPicUrl()
