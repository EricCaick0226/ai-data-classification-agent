# Day 8 笔记：普通 Pipeline 测试

1. 今天的 main.py 不是 Agent，它只是把已有工具按固定顺序串起来。
2. analyze_csv 负责读取 CSV 并提取字段信息。
3. classify_column 负责分类字段，generate_report 负责生成 Markdown 报告。