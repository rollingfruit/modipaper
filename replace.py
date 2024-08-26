import json
import re
import pypandoc

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_markdown(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def replace_comments(markdown_content, comments):
    # 将评论列表转换为字典，以 ID 为键
    comment_dict = {comment['id']: comment for comment in comments}
    print(f"comment_dict:\n ---\n{comment_dict}\n ---\n")

    def replace_single_comment(match):
        comment_start = match.group(1)
        old_text = match.group(2)
        comment_end = match.group(3)
        
        # 提取评论 ID
        id_match = re.search(r'id="(\d+)"', comment_start)
        print(f"id_match in replace_single_comment:\n ---\n{id_match}\n ---\n")
        if id_match:
            comment_id = id_match.group(1)
            print(f"comment_id in replace_single_comment:\n ---\n{comment_id}\n ---\n")
            if comment_id in comment_dict:
                print(f"comment_id in comment_dict in replace_single_comment:\n ---\n{comment_id}\n ---\n")
                comment = comment_dict[comment_id]
                print(f"comment in replace_single_comment:\n ---\n{comment}\n ---\n")
                new_text = comment.get('comment_text_modified', old_text)
                print(f"new_text in replace_single_comment:\n ---\n{new_text}\n ---\n")
                
                # 递归替换嵌套评论
                new_text = replace_comments(new_text, comments)
                
                print(f'Replacing comment {comment_id}:')
                print(f'Old: {old_text}')
                print(f'New: {new_text}')
                print()
                
                return f"{comment_start}{new_text}{comment_end}"
        
        # 如果没有找到匹配的评论，返回原文
        print(f"No comment found for ID {comment_id}")
        return match.group(0)

    # 使用正则表达式替换评论
    pattern = re.compile(r'(\{\.comment-start.*?\})(.*?)(\[\].*?\.comment-end.*?\})', re.DOTALL)
    return pattern.sub(replace_single_comment, markdown_content)


def convert_markdown_to_docx(markdown_file, docx_file):
    # 使用pypandoc将Markdown转换为Word文档，并正确处理LaTeX数学公式
    pypandoc.convert_file(
        markdown_file,
        'docx',
        outputfile=docx_file,
        extra_args=[
            '--standalone',
            '--wrap=none',
            '--mathml',  # 使用MathML来渲染数学公式
            # '--pdf-engine=xelatex',  # 使用XeLaTeX引擎
            # '--webtex',  # 使用WebTeX来渲染数学公式
            # '--filter', 'pandoc-crossref',  # 如果使用了交叉引用
            '--citeproc'  # 如果使用了引用
        ]
    )
    # # 首先将Markdown转换为LaTeX
    # latex_content = pypandoc.convert_file(
    #     markdown_file,
    #     'latex',
    #     extra_args=['--standalone', '--wrap=none']
    # )
    
    # # 然后将LaTeX转换为Word
    # pypandoc.convert_text(
    #     latex_content,
    #     'docx',
    #     format='latex',
    #     outputfile=docx_file,
    #     extra_args=['--standalone', '--wrap=none']
    # )
    print(f"已将 {markdown_file} 转换为 {docx_file}，包括LaTeX数学公式")

def replace_and_to_docx(markdown_file, json_file_modified, output_file, output_file_docx):

    markdown_content = load_markdown(markdown_file)
    comments_modified = load_json(json_file_modified)
    # print(f"comments_modified in json_file_modified:\n ---\n{comments_modified}\n ---\n")

    modified_content = replace_comments(markdown_content, comments_modified)

    save_markdown(output_file, modified_content)
    print(f"Modified content saved to {output_file}")

    # md -> docx
    convert_markdown_to_docx(output_file, output_file_docx)

if __name__ == "__main__":

    # 替换md、转为docx
    markdown_file = "./temp_files/说明书_修改2024-08-26-with-comments.md"
    json_file_modified = "./temp_files/说明书_修改2024-08-26_comments_modified.json"
    output_file = "./temp_files/说明书_修改2024-08-26_comments_modified.md"
    output_file_docx = "./说明书_修改2024-08-26_comments_modified.docx"
    replace_and_to_docx(markdown_file, json_file_modified, output_file, output_file_docx)

    # 只转为docx
    # markdown_file_by_hand = "./temp_files/test_2_modify_by_hand.md"
    # output_file_docx_by_hand = "./files/test_with_comments_modified_by_hand.docx"
    # convert_markdown_to_docx(markdown_file_by_hand, output_file_docx_by_hand)