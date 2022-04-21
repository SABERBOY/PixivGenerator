from pprint import pformat
import sys
from typing import List
import requests
import re
import os
import datetime
import json

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'referer': 'https://www.pixiv.net/ranking.php?mode=daily&content=illust',
}

PixivPath = './pixiv/'
repeat = 1
repeat_user_name = 1


def getSinglePic(url, picPath):
    global repeat
    global repeat_user_name
    proxies = get_proxy()
    response = requests.get(url, headers=headers, proxies=proxies)
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
        user_name = re.sub('[\\\ \/ \* \? \" \: \< \> \|]',
                           str(repeat_user_name), user_name)
        repeat_user_name += 1
    # 提取图片原图地址
    picture = re.search('"original":"(.+?)"},"tags"', response.text)
    pic = requests.get(picture.group(1), headers=headers, proxies=proxies)
    f = open(picPath + '%s_%s-by-%s.%s' %
             (illust_id, name, user_name, picture.group(1)[-3:]), 'wb')
    f.write(pic.content)
    f.close()
    return True


def generateJson(picPath: str):
    # generate one picPath json file
    generate_one_json(picPath)

    # generate other json file
    path = PixivPath
    dirs_all = os.listdir(path)
    for dir in dirs_all:
        pd = path+dir
        if os.path.isdir(pd):
            # json_file = get_file_list(pd+"/", ['.json'])
            generate_one_json(pd+"/")

    # generate url.json file with other json file url
    pixivPath = path
    pixivJsonPath = path+'url.json'
    path = [os.path.join(dp, f) for dp, dn, fs in os.walk(pixivPath) for f in fs if
            os.path.splitext(f)[1] in ['.json']]
    path = [i for i in path if i.find(pixivJsonPath) == -1]
    pixiv_json = {"pixiv": path}
    jj = json.dumps(pixiv_json)
    f = open(pixivJsonPath, 'wb')
    f.write(jj.encode())
    f.close()

# generate one picPath json file


def generate_one_json(picPath):
    file_path = get_file_list(picPath, ['.jpg', '.png'])
    pixiv_json = {"pixiv_pic": file_path}
    pixiv_json_path = picPath+'pixiv_pic.json'
    pixiv_json_file = open(pixiv_json_path, 'wb')
    pixiv_json_file.write(json.dumps(pixiv_json).encode())
    pixiv_json_file.close()


def get_file_list(path: str, file_ext: List[str]) -> List[str]:
    file_list: List[str] = [os.path.join(dp, f) for dp, dn, fs in os.walk(path) for f in fs if
                            os.path.splitext(f)[1] in file_ext]
    return file_list


def get_proxy():
    proxies = {
        'http': 'http://127.0.0.1:11000',
        'https': 'http://127.0.0.1:11000'
    }
    proxies = None
    return proxies


def getAllPicUrl():
    count = 1
    dataTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    proxies = get_proxy()
    picPath = PixivPath+dataTime+'/'
    for n in range(1, 2):
        url = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%d&format=json' % n
        response = requests.get(url, headers=headers, proxies=proxies)
        illust_id = re.findall('"illust_id":(\d+?),', response.text)
        if not os.path.exists(picPath):
            os.makedirs(picPath)
        picUrl = ['https://www.pixiv.net/artworks/' + i for i in illust_id]
        for url in picUrl:
            print('Downloading the picture %d ' % count, end='   ')
            print('OK' if getSinglePic(url, picPath) else "FAILED", end='\n')
            count += 1
    # os.system("ls -al")
    generateJson(picPath)
    return None


getAllPicUrl()

""" dirs_all = os.listdir(path)
for dir in dirs_all:
    pd = path+dir
    if os.path.isdir(pd):
        print(pd)
        json_file = get_file_list(pd+"/", ['.json'])
        print(json_file)
        generate_one_json(pd+"/") """

""" pixivPath = PixivPath
pixivJsonPath = PixivPath+'url.json'
path = [os.path.join(dp, f) for dp, dn, fs in os.walk(pixivPath) for f in fs if
        os.path.splitext(f)[1] in ['.json']]
path = [i for i in path if i.find(pixivJsonPath) == -1]
pixiv_json = {"pixiv": path}
jj = json.dumps(pixiv_json)
print(jj)
print(pixivJsonPath != "./pixiv/url.json") """
