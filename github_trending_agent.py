import requests
import os
from datetime import datetime, timedelta
from googletrans import Translator

def get_trending_github_repos_markdown():
    # 计算昨天和今天的日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_range_str = f"{yesterday.strftime('%Y-%m-%d')}..{today.strftime('%Y-%m-%d')}"

    # GitHub API endpoint
    url = "https://api.github.com/search/repositories"

    # 查询参数：昨天到今天创建，按star数量降序排列，每页10个
    params = {
        "q": f"created:{date_range_str}",
        "sort": "stars",
        "order": "desc",
        "per_page": 10
    }

    translator = Translator() # Initialize translator

    # 获取GitHub PAT
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    else:
        # 在这里不打印警告，因为这个脚本的输出会被捕获
        pass

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 如果请求不成功，抛出HTTPError
        data = response.json()

        items = data.get("items", [])

        markdown_content = f"# GitHub {yesterday.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')} 热门项目\n\n"

        if not items:
            markdown_content += f"在 {yesterday.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')} 未找到热门GitHub项目.\n"
        else:
            for i, item in enumerate(items):
                if item['stargazers_count'] >= 50: # Filter by star count
                    markdown_content += f"## {i+1}. {item['name']}\n"
                    markdown_content += f"- **URL:** {item['html_url']}\n"
                    markdown_content += f"- **Stars:** {item['stargazers_count']}\n"
                    description = item['description'] or '无描述'
                    markdown_content += f"- **Description:** {description}\n"
                    try:
                        translated_description = translator.translate(description, dest='zh-cn').text
                        markdown_content += f"- **Description_zh:** {translated_description}\n\n"
                    except Exception as e:
                        markdown_content += f"- **Description_zh:** 翻译失败: {e}\n\n"
        
        # Add a separator for the next section
        markdown_content += f"\n---\n\n"

        # Calculate date range for past month
        one_month_ago = today - timedelta(days=30)
        month_date_range_str = f"{one_month_ago.strftime('%Y-%m-%d')}..{today.strftime('%Y-%m-%d')}"

        # Query parameters for past month trending repos
        month_params = {
            "q": f"created:{month_date_range_str}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }

        try:
            month_response = requests.get(url, params=month_params, headers=headers)
            month_response.raise_for_status()
            month_data = month_response.json()
            month_items = month_data.get("items", [])

            markdown_content += f"# GitHub {one_month_ago.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')} 热门项目 (Star >= 200)\\n\\n"

            if not month_items:
                markdown_content += f"在 {one_month_ago.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')} 未找到热门GitHub项目.\\n"
            else:
                for i, item in enumerate(month_items):
                    if item['stargazers_count'] >= 200: # Filter by star count
                        markdown_content += f"## {i+1}. {item['name']}\\n"
                        markdown_content += f"- **URL:** {item['html_url']}\\n"
                        markdown_content += f"- **Stars:** {item['stargazers_count']}\\n"
                        description = item['description'] or '无描述'
                        markdown_content += f"- **Description:** {description}\\n"
                        try:
                            translated_description = translator.translate(description, dest='zh-cn').text
                            markdown_content += f"- **Description_zh:** {translated_description}\\n\\n"
                        except Exception as e:
                            markdown_content += f"- **Description_zh:** 翻译失败: {e}\\n\\n"

        except requests.exceptions.RequestException as e:
            markdown_content += f"请求GitHub API (过去一月) 时发生错误: {e}\\n"
        except Exception as e:
            markdown_content += f"处理响应 (过去一月) 时发生错误: {e}\\n"

        return markdown_content

    except requests.exceptions.RequestException as e:
        return f"请求GitHub API时发生错误: {e}\\n"
    except Exception as e:
        return f"处理响应时发生错误: {e}\\n"

if __name__ == "__main__":
    print(get_trending_github_repos_markdown())
