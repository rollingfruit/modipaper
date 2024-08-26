import pypandoc
import json
import re
import os


if not pypandoc.get_pandoc_path():
    pypandoc.download_pandoc()
    os.environ.setdefault('PYPANDOC_PANDOC', pypandoc.get_pandoc_path())


def convert_docx_to_markdown(docx_file, markdown_file_with_comments, markdown_file_without_comments):

    pypandoc.convert_file(
        docx_file,
        'markdown',
        outputfile=markdown_file_with_comments,
        extra_args=['--standalone', '--wrap=none', '--track-changes=all', '--extract-media=.']
    )
    
    # 生成不含批注的Markdown
    pypandoc.convert_file(
        docx_file,
        'markdown',
        outputfile=markdown_file_without_comments,
        extra_args=['--standalone', '--wrap=none', '--track-changes=accept', '--extract-media=.']
    )



def extract_comments(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    comment_pattern = re.compile(r'\[(.+?)\]\{\.comment-start id="(\d+)" author="([^"]+)" date="([^"]+)"\}(.*?)\[\]\{\.comment-end id="\2"\}', re.DOTALL)

    def extract_nested(text, parent_id=None, depth=0):
        comments = []
        for match in comment_pattern.finditer(text):
            commented_text = match.group(1).strip()
            comment_id = match.group(2)
            author = match.group(3)
            date = match.group(4)
            comment_text = match.group(5).strip()

            # 提取当前评论
            current_comment = {
                "id": comment_id,
                "parent_id": parent_id,
                "author": author,
                "date": date,
                "commented_text": commented_text,
                "comment_text": comment_text,
                "depth": depth,
                "full_match": match.group(0)
            }
            # 处理短评论（无解，因为full_match没包含更多内容，当前匹配不到更多上下文，所以无法添加更多上下文）
            # if len(comment_text) < 10:

            comments.append(current_comment)

            # 递归提取嵌套的评论
            nested_comments = extract_nested(comment_text, comment_id, depth + 1)
            
            # 更新当前评论的文本，移除嵌套评论
            if nested_comments:
                for nested in nested_comments:
                    current_comment["comment_text"] = current_comment["comment_text"].replace(nested["full_match"], "").strip()

            comments.extend(nested_comments)
            last_end = match.end()

        return comments

    # 提取所有评论并按ID排序
    all_comments = extract_nested(content)
    all_comments.sort(key=lambda x: int(x["id"]))

    return all_comments


def get_comments_json(docx_file, markdown_file_with_comments, markdown_file_without_comments, comment_file):
    # 转换为Markdown（包含和不包含批注）
    convert_docx_to_markdown(docx_file, markdown_file_with_comments, markdown_file_without_comments)
    
    # 提取批注
    comments = extract_comments(markdown_file_with_comments)
    
    # 保存为JSON
    with open(comment_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    print("批注提取完成")

if __name__ == "__main__":
    file_dir = "./files/"
    file_name = "test"
    # file_name = "test_2"
    docx_file = f"{file_name}.docx"
    markdown_file_with_comments = f"{file_dir}dealing/{file_name}-with-comments.md"
    markdown_file_without_comments = f"{file_dir}dealing/{file_name}-without-comments.md"
    comment_file = f"{file_dir}dealing/{file_name}_comments.json"

    get_comments_json(docx_file, markdown_file_with_comments, markdown_file_without_comments, comment_file)

