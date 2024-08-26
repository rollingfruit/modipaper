import streamlit as st
import os
import time
from agent import modify_by_ai
from replace import replace_and_to_docx
from prase import get_comments_json

def process_document(uploaded_file):
    # 创建一个临时目录来存储文件
    temp_dir = "temp_files/"
    os.makedirs(temp_dir, exist_ok=True)

    # 保存上传的文件
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 设置文件路径
    file_name = os.path.splitext(uploaded_file.name)[0]
    markdown_file_with_comments = os.path.join(temp_dir, f"{file_name}-with-comments.md")
    markdown_file_without_comments = os.path.join(temp_dir, f"{file_name}-without-comments.md")
    comment_file = os.path.join(temp_dir, f"{file_name}_comments.json")
    json_file_modified = os.path.join(temp_dir, f"{file_name}_comments_modified.json")
    output_file = os.path.join(temp_dir, f"{file_name}_with_comments_modified.md")
    output_file_docx = os.path.join(temp_dir, f"{file_name}_with_comments_modified.docx")

    # 处理文档
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 第一步：转换DOCX并提取评论
    status_text.text("正在转换DOCX并提取评论...")
    get_comments_json(file_path, markdown_file_with_comments, markdown_file_without_comments, comment_file)
    progress_bar.progress(0.1)  # 10%的进度

    # 第二步：使用AI修改评论
    status_text.text("正在使用AI修改评论...")
    def update_progress(progress):
        # 确保进度值在0到1之间
        progress = max(0, min(1, 0.1 + progress * 0.8))  # AI修改占80%的进度
        progress_bar.progress(progress)
        status_text.text(f"正在使用AI修改评论...修改进度: {int(progress * 100)}%")

    modify_by_ai(markdown_file_without_comments, comment_file, json_file_modified, update_progress)

    # 第三步：替换评论并转换回DOCX
    status_text.text("正在替换评论并转换回DOCX...")
    replace_and_to_docx(markdown_file_with_comments, json_file_modified, output_file, output_file_docx)
    progress_bar.progress(1.0)  # 100%完成

    status_text.text("处理完成！")

    return output_file_docx

def main():
    st.title("DOCX批注改稿")
    st.write("上传一个包含批注的DOCX文件，使用AI修改内容。")

    uploaded_file = st.file_uploader("选择一个DOCX文件", type="docx")

    if uploaded_file is not None:
        if st.button("处理文档"):
            with st.spinner("处理中..."):
                output_file = process_document(uploaded_file)

            st.success("文档处理成功！")
            
            with open(output_file, "rb") as file:
                st.download_button(
                    label="下载已修改的DOCX",
                    data=file,
                    file_name="modified_document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

if __name__ == "__main__":
    main()