import json
import os
from openai import OpenAI
import logging
from tqdm import tqdm

# 设置日志的基本配置，日志将被写入到example.log文件中
logging.basicConfig(filename='./data/agent.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(
    # This is the default and can be omitted
    api_key="sk-sKg00f4ee80d57ae6c1c8326c055b880154b240b352Qg6y8",
    base_url="https://api.gptsapi.net/v1",
)

def load_paper(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def agent1_reviewer(paper, comment_text, commented_text):
    prompt = f"""作为论文审稿人,请根据以下信息:
        整篇论文内容: {paper}
        被标注的内容: {comment_text}
        老师的批注: {commented_text}
        请反思被标注内容的合理性, 理解老师的批注要求，给出1~2点明确的修改建议。
    请直接输出修改建议,不要有其他额外的文字。"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "你是一位经验丰富的论文审稿人。"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def agent2_expert(paper, comment_text, commented_text_by_ai):
    prompt = f"""作为学术专家,请根据以下信息:
        整篇论文内容: {paper}
        被标注的内容: {comment_text}
        审稿人的建议: {commented_text_by_ai}
        请修改被标注的内容。直接输出修改后的内容, 尽量不要在字数上比被标注的内容多太多，而是在内容上优化、来满足建议, 不要有其他额外的文字。"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "你是一位学术领域的专家。"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def modify_by_ai(markdown_file_without_comments, comment_file, json_file_modified, progress_callback=None):
    paper = load_paper(markdown_file_without_comments)
    comments = load_comments(comment_file)

    total_comments = len(comments)
    for i, comment in enumerate(comments):
        logging.info("## 被标注的内容: {}".format(comment['comment_text'].replace('\n', ' ')))
        # Agent1: 审稿人
        commented_text_by_ai = agent1_reviewer(paper, comment["comment_text"], comment["commented_text"])
        comment["commented_text_by_ai"] = commented_text_by_ai
        logging.info("AI的建议: {}".format(comment['commented_text_by_ai'].replace('\n', ' ')))
        # Agent2: 学术专家
        comment_text_modified = agent2_expert(paper, comment["comment_text"], commented_text_by_ai)
        comment["comment_text_modified"] = comment_text_modified
        logging.info("修改后的内容: {}".format(comment['comment_text_modified'].replace('\n', ' ')))

        # 更新进度
        if progress_callback:
            progress_callback((i + 1) / total_comments)

    # 保存修改后的JSON
    with open(json_file_modified, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)