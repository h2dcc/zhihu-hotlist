# 知乎热榜自动抓取

使用 GitHub Actions 定时抓取 [知乎热榜聚合页](https://tophub.today/n/mproPpoq6O)，
并将结果保存到仓库根目录：

- `zhihu-hotlist.txt`：纯文本格式
- `zhihu-hotlist.xml`：XML 格式

## 工作原理

- Python + requests + BeautifulSoup 解析 `tr td.al a` 元素
- GitHub Actions 每天北京时间 06:00 和 18:00 自动运行
- 有变化时自动 commit 并 push 到当前仓库

## 本地运行

```bash
pip install -r requirements.txt
python fetch_zhihu_hotlist.py
```

## 手动触发

在 GitHub 仓库的 Actions 页面选择 **Update Zhihu Hotlist** 工作流，点击 **Run workflow**。
