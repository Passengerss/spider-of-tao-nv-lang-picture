# -*- coding : utf-8 -*-
'''
Desc: 抓取淘宝中淘女郎模特的信息：

    名字,图片,身高，体重
    以文件夹形式保存
    信息保存为文本
    通过观察network 中变化，得出信息网址：https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8

    经过分析发现，无法通过此网站源码中链接实现翻页，于是想到通过提交表单数据实现翻页。request url 不变

    然后就是如何进入 各位模特的详情页 的问题了。通过观察发现：
    https://mm.taobao.com/self/aiShow.htm?&userId=268367415  可以进入对应模特的个人界面。
    https://mm.taobao.com/self/model_info.htm?user_id=268367415  可以进入对应model的模特卡，里面有跟多相关信息。
    而 userId 正好我们可以从前面那个链接获取到。通过改变ID便可实现对详情页面信息的爬取
'''
import urllib.request
import urllib.parse
import re
from user_agent.base import generate_user_agent
import os.path, os
from datetime import datetime
import threading
# 设立标志位flag 用于判断文件是否已经存在，用来避免重复操作
global flag
class Spider:
    def __init__(self):
        pass

    # 定义常用的 URL 打开函数
    def open_url(self, url, data):
        data = urllib.parse.urlencode(data).encode("utf-8")
        user_agent = generate_user_agent()
        header = {"User-Agent":user_agent}
        req = urllib.request.Request(url, data=data, headers=header)
        response = urllib.request.urlopen(req).read() # 文件未进行decode解码，此时为response二进制文件
        return response

    # 获取model的realname
    def get_realname(self, url, data):
        response = self.open_url(url, data).decode('gbk').encode('utf-8').decode('utf-8')
        name = re.compile('realName":"(.*?)"').findall(response)
        return name

    # 获取model头像地址，并返回图片的二进制信息
    def get_head(self, url,data):
        response = self.open_url(url,data).decode('gbk').encode('utf-8').decode('utf-8')
        link_list = re.compile('avatarUrl":"(.*?)"').findall(response)
        imgs = []
        for link in link_list:
            link_ = 'http:'+ link
            img = urllib.request.urlopen(link_).read()
            imgs.append(img)
        return imgs               # 直接返回二进制文件，方便图片保存

    # 保存一张图片
    def save_img(self, img, folder, picname, i):
        print("正在保存 %s 的照片..." %picname)
        with open(folder+'/'+picname+'.jpg', 'wb') as f:
            f.write(img)
        print("完成！")

    # 获取model的 城市，身高，体重，被赞次数
    def get_desc(self,url, data):
        response = self.open_url(url,data).decode('gbk').encode('utf-8').decode('utf-8')
        city = re.compile('city":"(.*?)"').findall(response)
        height = re.compile('height":"(.*?)"').findall(response)
        weight = re.compile('weight":"(.*?)"').findall(response)
        favor = re.compile('totalFavorNum":(.*?),').findall(response)
        # 建立人物信息对应关系
        desc = list(zip(city, height, weight, favor))
        return desc

    # 保存一个人物信息
    def save_desc(self, folder, filename, desc, i):
        print("正在保存 %s 的个人信息" %filename)
        line = "model：\t\t %s \n\n所在城市：\t\t %s \n\n身高(cm)：\t\t %s \n\n体重(kg)：\t\t %s \n\n这货被赞过： %d 次" % (
        filename, desc[i][0], (desc[i][1]), (desc[i][2]), int(desc[i][3]))

        with open(folder + '/' + filename + '.txt', 'w') as f:
            f.write(line)
        print("完成！")


    # 建立每个模特的文件夹
    def make_dir(self, folder):
        #判断model文件夹下是否存在folder
        if os.path.exists(folder):
            print("文件夹已存在！")
            flag = 1
            return flag
        else:
            os.mkdir(folder)
            print("已创建文件夹 %s " % folder)
            flag = 0
            return flag

    def main(self):
        url = "https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8"
        print(datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ))
        pages = int(input("程序开始...\n请输入要爬取的页数(1-1450):\n" ))
        if pages<1:
            print("太小啦，请输入1-1450之间的整数...")
        if pages>1450:
            print("太大啦，请输入1-1450之间的整数...")
        i = 0
        # 选择一个文件夹
        os.chdir("model")

        # 实现翻页操作
        for page in range(1,pages+1):
            data = {'currentPage': page, 'pageSize':100}
            # 重置i 因为每一页只有30份数据
            i =0
            # 获取人物基本信息
            real_name = self.get_realname(url, data)
            imgs = self.get_head(url, data)
            desc = self.get_desc(url, data)
            # 围绕名字这个关键字来理清思路
            for name in real_name:
                flag = self.make_dir(name)
                if flag == 0:
                    print("正在进行第 %d 页的第 %d 次操作，操作对象是： %s " % (page, i + 1, name))
                    # 保存model头像的二进制文件
                    self.save_img(imgs[i], name, name, i)
                    self.save_desc(name, name, desc, i)
                else:
                    pass
                i += 1
        print("It's done!!\n", datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ))

if __name__ == "__main__":
    spider = Spider()
    spider.main()
