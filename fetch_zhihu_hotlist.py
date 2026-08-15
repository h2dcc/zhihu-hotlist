#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取知乎热榜并生成 XML / TXT 文件。

数据来源: https://tophub.today/n/mproPpoq6O
选择器: tr td.al a
"""

import datetime
import sys
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://tophub.today/n/mproPpoq6O"
TXT_FILE = "zhihu-hotlist.txt"
XML_FILE = "zhihu-hotlist.xml"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def fetch_hotlist():
    """请求页面并返回 [(rank, title, url), ...]"""
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    # 如果服务端没有明确编码，或 requests 把编码识别为 ISO-8859-1，
    # 再用 apparent_encoding 兜底；否则保留响应头里的 charset（通常是 utf-8）。
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for tr in soup.select("tr"):
        a = tr.select_one("td.al a")
        if not a:
            continue
        title = a.get_text(strip=True)
        url = a.get("href", "").strip()
        if not title:
            continue
        # 页面可能按顺序排列，这里按出现顺序编号，避免解析不到显式序号
        rank = len(items) + 1
        # 有些链接是相对地址，补全为绝对地址
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://tophub.today" + url
        items.append((rank, title, url))
    return items


def generate_txt(items, generated_at):
    lines = [f"知乎热榜（生成时间：{generated_at}）", ""]
    for rank, title, url in items:
        lines.append(f"{rank}. {title}")
        if url:
            lines.append(f"   {url}")
    return "\n".join(lines) + "\n"


def generate_xml(items, generated_at):
    root = ET.Element("zhihu-hotlist", generated=generated_at, source=SOURCE_URL)
    for rank, title, url in items:
        item = ET.SubElement(root, "item")
        ET.SubElement(item, "rank").text = str(rank)
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "url").text = url
    xml_bytes = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    # ElementTree 默认输出单引号，这里保留即可；如需更美观可以格式化
    return xml_bytes.decode("utf-8") + "\n"


def main():
    try:
        items = fetch_hotlist()
    except Exception as exc:
        print(f"抓取失败: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("未解析到任何热榜条目，请检查页面结构是否变化。", file=sys.stderr)
        return 1

    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(TXT_FILE, "w", encoding="utf-8") as f:
        f.write(generate_txt(items, generated_at))

    with open(XML_FILE, "w", encoding="utf-8") as f:
        f.write(generate_xml(items, generated_at))

    print(f"成功生成 {len(items)} 条热榜：{TXT_FILE}、{XML_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
