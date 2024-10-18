from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from threading import Lock
from time import time
from glob import glob
from re import sub
import requests


# 多线程并发模块
def multi_thread():
    with ThreadPoolExecutor() as pool:
        pool.map(check_url_availability, url_list[:len(url_list)])


# 检测单个URL的可用性
def check_url_availability(url):
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if 300 <= response.status_code < 400:
            redirect_url = response.headers.get('Location')
            with thread_lock:
                print(f"已重定向：{name_list[url_list.index(url)]}【{url}】 -> 【{redirect_url}】")
        elif 200 <= response.status_code < 400:
            with thread_lock:
                print(f"可用：{name_list[url_list.index(url)]}【{url}】")
        else:
            with thread_lock:
                print(f"不可用：{name_list[url_list.index(url)]}【{url}】 -> 【{response.status_code}】")
    except requests.RequestException as e:
        with thread_lock:
            print(f"异常：{name_list[url_list.index(url)]}【{url}】 -> 【{type(e).__name__} - {e}】")


# 查找当前目录下名称包含“免费GalGame资源站目录”的.html文件
file_path = glob("*免费GalGame资源站目录*.html")
if file_path:
    with open(file_path[0], "r", encoding="utf-8") as file:
        html_content = file.read()
    # 解析HTML内容
    soup = BeautifulSoup(html_content, "html.parser")
    url_list = []
    name_list = []
    # 提取第一个<dl>部分中的所有链接
    first_dl = soup.find("dl")
    if first_dl:
        for a in first_dl.find_all("a", href=True):
            if "github" not in a['href']:
                url_list.append(a['href'])
                name_list.append(sub(r'【.*?】', '', a.text))
    else:
        print("资源错误，请重新下载相关资源")
    print(f"已收集 {len(url_list)} 个站点")
    # 启动多线程并发模块
    thread_lock = Lock()
    start = time()
    multi_thread()
    end = time()
    time = round(end - start, 2)
    with thread_lock:
        print(f"耗时：{time}s")
else:
    print("未找到指定的.html文件")
