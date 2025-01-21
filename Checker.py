from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from re import compile, DOTALL
from time import time
import cloudscraper


def sections_extract(markdown_text):
    pattern = compile(r"###\s+(.*?)\n(.*?)(?=(\n###|\Z))", DOTALL)
    matches = pattern.findall(markdown_text)
    sections = []
    for match in matches:
        title = match[0].strip()
        sections.append(title)
    return sections


# 提取README.md中的URL
def content_extractor():
    input_file = "README.md"
    current_section = None
    result = {}
    # 读取Markdown文档
    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()
        file.seek(0)
        lines = file.readlines()
    # 提取标题
    sections = sections_extract(text)
    link_pattern = compile(r"- \[([^]]+)]\((https?://[^)]+)\)")
    # 解析文档
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
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.head(site, timeout=10, allow_redirects=True)
        if 200 <= response.status_code < 400:
            with thread_lock:
                _section_ = section_map[site]  # 获取所属分区
                print(f"可用：【{_section_}】{name_list[url_list.index(site)]} -> 【{site}】")
        else:
            with thread_lock:
                _section_ = section_map[site]  # 获取所属分区
                print(f"异常：【{_section_}】{name_list[url_list.index(site)]} -> 【{site}】 -> 【{response.status_code}】")
    except Exception as e:
        with thread_lock:
            _section_ = section_map[site]  # 获取所属分区
            print(f"异常：【{_section_}】{name_list[url_list.index(site)]} -> 【{site}】 -> 【{type(e).__name__} - {e}】")


# 读取.md文件并统计所有站点数量
site_data = content_extractor()
total_sites = sum(len(sites) for sites in site_data.values())

# 选择需要读取的栏目
while True:
    print(f"可选栏目（已发现 {total_sites} 个站点）：")
    available_sections = list(site_data.keys())
    for i, section in enumerate(available_sections):
        section_site_count = len(site_data[section])
        print(f"{i + 1}. {section}（{section_site_count}个）")
    selected_indices = input("请输入需要读取的栏目编号（用空格分隔）：").split()
    # 验证输入并提取所选栏目
    if all(index.isdigit() and 1 <= int(index) <= len(available_sections) for index in selected_indices):
        selected_sections = [available_sections[int(index) - 1] for index in selected_indices]
        break
    else:
        print("输入错误，请输入有效的栏目编号")

# 提取所选栏目的站点信息
url_list = []
name_list = []
section_map = {}  # 映射站点URL到所属分区
for section in selected_sections:
    for name, url in site_data[section].items():
        url_list.append(url)
        name_list.append(name)
        section_map[url] = section  # 保存站点所属分区

# 启动多线程检测
if url_list:
    print(f"正在检查 {len(url_list)} 个站点……")
    thread_lock = Lock()
    start = time()
    with ThreadPoolExecutor() as pool:
        pool.map(checker, url_list)
    end = time()
    elapsed_time = round(end - start, 2)
    print(f"耗时：{elapsed_time}s")
else:
    print("未找到任何站点信息")
