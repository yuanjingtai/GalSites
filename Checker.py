from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from time import time
import requests
import re


# 提取README.md中的URL
def extractor():
    # 定义输入和输出文件
    input_file = "README.md"
    # 定义需要提取的部分标题
    sections = ["主要站点", "Telegram频道", "暂存区"]
    # 正则表达式匹配链接
    link_pattern = re.compile(r"- \[([^]]+)]\((https?://[^)]+)\)")
    # 存储提取的结果
    result = {}
    # 读取并解析Markdown文件
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    current_section = None
    for line in lines:
        # 检测当前段落是否为目标部分
        for item in sections:
            if line.strip().startswith(f"### {item}"):
                current_section = item
                result[current_section] = {}
                break
        # 如果当前段落属于目标部分，提取链接
        if current_section and line.startswith("- ["):
            match = link_pattern.match(line)
            if match:
                names, urls = match.groups()
                result[current_section][names] = urls
    return result


# URL检测模块
def checker(site):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        response = requests.head(site, timeout=10, allow_redirects=True, headers=headers)
        if 300 <= response.status_code < 400:
            redirect_url = response.headers.get('Location', '未知重定向地址')
            with thread_lock:
                print(f"已重定向：{name_list[url_list.index(site)]}【{site}】 -> 【{redirect_url}】")
        elif 200 <= response.status_code < 400:
            with thread_lock:
                print(f"可用：{name_list[url_list.index(site)]}【{site}】")
        else:
            with thread_lock:
                print(f"不可用：{name_list[url_list.index(site)]}【{site}】 -> 【{response.status_code}】")
    except requests.RequestException as e:
        with thread_lock:
            print(f"异常：{name_list[url_list.index(site)]}【{site}】 -> 【{type(e).__name__} - {e}】")


# 读取.md文件并统计所有站点数量
site_data = extractor()
total_sites = sum(len(sites) for sites in site_data.values())

# 选择需要读取的栏目（请不要在这里点炒饭！！！）
while True:
    print(f"可选栏目（已发现 {total_sites} 个站点）：")
    available_sections = list(site_data.keys())
    for i, section in enumerate(available_sections):
        section_site_count = len(site_data[section])  # 每个栏目的站点数量
        print(f"{i + 1}. {section}（{section_site_count}个）")
    selected_indices = input("请输入需要读取的栏目编号（用空格分隔）：").split()

    # 验证输入并提取所选栏目
    if all(index.isdigit() and 1 <= int(index) <= len(available_sections) for index in selected_indices):
        selected_sections = [available_sections[int(index) - 1] for index in selected_indices]
        break  # 输入合法，跳出循环
    else:
        print("输入错误，请输入有效的栏目编号")

# 提取所选栏目的站点信息
url_list = []
name_list = []
for section in selected_sections:
    for name, url in site_data[section].items():
        url_list.append(url)
        name_list.append(name)
# 启动多线程检测
if url_list:
    print(f"正在检查 {len(url_list)} 个站点……")
    thread_lock = Lock()
    start = time()
    # 开启多线程并发
    with ThreadPoolExecutor() as pool:
        pool.map(checker, url_list)
    end = time()
    elapsed_time = round(end - start, 2)
    print(f"耗时：{elapsed_time}s")
else:
    print("未找到任何站点信息")
