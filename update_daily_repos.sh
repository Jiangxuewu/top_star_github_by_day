#!/bin/bash

# 切换到脚本所在的目录
cd "$(dirname "$0")"

# 获取昨天和今天的日期
TODAY_DATE=$(date +"%Y-%m-%d")
YESTERDAY_DATE=$(date -v -1d +"%Y-%m-%d") # For macOS/BSD date command

# 运行Python脚本并捕获其输出
# 注意：这里假设github_trending_agent.py会打印Markdown内容到stdout
REPO_MARKDOWN=$(python3 github_trending_agent.py)

# 检查README.md是否存在，如果不存在则创建
if [ ! -f "README.md" ]; then
    echo "# GitHub Daily Trending Repositories" > README.md
fi

# 将今天的日期作为一级标题添加到README.md
echo -e "\n# ${TODAY_DATE} GitHub Daily Trending Repositories\n" >> README.md
echo -e "${REPO_MARKDOWN}" >> README.md

# Git 操作
git add README.md
git commit -m "Update daily trending repos for ${YESTERDAY_DATE} to ${TODAY_DATE} - Gemini-cli"
git push origin main

echo "Daily trending repositories updated and pushed to GitHub."
