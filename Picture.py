# -*- coding : utf-8 -*-
'''
Desc: 抓取淘宝中淘女郎首页的信息：
    名字,图片
    通过观察network 中变化，得出信息网址：https://mm.taobao.com/alive/list.do?scene=all&page=1
    page 为页码
'''

# --------------需要补全异常处理机制，不然会出现一个失败而影响整个函数运行---------------------
# 等下再补充
import urllib.request
import re
from user_agent.base import generate_user_agent



class Spider:
    # 定义需要爬取的页数
    def __init__(self, page):
        self.page = int(page)

     # 获取要爬取的图片的页数
    def get_pags(self, page):
        for i in range(1, page+1):
            url = "https://mm.taobao.com/alive/list.do?scene=all&page=%d"%i
            yield url

    # 定义常用的 URL 打开函数
    def open_url(self, url):
        user_agent = generate_user_agent()
        header = {"User-Agent":user_agent}
        req = urllib.request.Request(url, headers=header)
        response = urllib.request.urlopen(req).read() # 文件未进行decode解码，此时为response二进制文件
        return response

    # 定义获取图片名称的函数
    def get_name(self, url):
        response = self.open_url(url).decode('gbk').encode('utf-8').decode('utf-8')
        name_list = re.compile('darenNick":"(.*?)"').findall(response)
        return name_list

    # 定义获取图片链接地址并返回图片内容
    def get_picture(self, url):
        response = self.open_url(url).decode('gbk').encode('utf-8').decode('utf-8')
        link_list = re.compile('avatarUrl":"(.*?)"').findall(response)
        for link in link_list:
            if re.compile('http:').match(link):
                img = self.open_url(link)
            else:
                link_ = 'http:'+ link
                img = self.open_url(link_)
            yield img               # 这里一个二进制生成器，方便图片保存

    # 保存图片
    def save_picture(self, url):
        name = self.get_name(url)
        img = self.get_picture(url)
        list_zip = list(zip(name, img))

        for each in list_zip:
            with open('./首页/%s.jpg'%each[0], 'wb') as f:
                f.write(each[1])


    def main(self):
        links = self.get_pags(self.page)
        for link in links:
            print(link)
            self.get_name(link)
            self.get_picture(link)
            self.save_picture(link)
        print("It's done!!")

if __name__ == "__main__":
    spider = Spider(67)
    spider.main()
