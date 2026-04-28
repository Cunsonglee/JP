import json
import os
import pandas as pd
import streamlit as st
from pathlib import Path

# 【更改 1】：移除全局变量 findic = {}，改为使用 Streamlit 的 session_state 或在函数内返回字典。
# 这里我们使用一个局部变量，通过函数返回值传递，更符合 Web 应用的安全规范。

def for_json(findic):
    # 【更改 2】：将原先操作全局变量的逻辑，改为修改传入的字典。
    def deal_json(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f).get("data", [])
            for i in data:
                findic[i["wordName"]] = i["wordDesc"]

    # 注意：此处为遍历当前脚本所在目录的所有 json
    for root, dirs, files in os.walk(os.path.dirname(__file__), topdown=False):
        for name in files:
            if name.endswith(".json") and name != "final.json":
                deal_json(os.path.join(root, name))
    return findic

def for_xlsx(findic):
    # 【更改 3】：将 tqdm 替换为 Streamlit 的进度条 st.progress
    if not os.path.exists("ABAB.xlsx"):
        st.warning("未找到 ABAB.xlsx 文件，已跳过。")
        return findic
        
    pd_frame = pd.read_excel("ABAB.xlsx")
    progress_bar = st.progress(0, text="正在处理 ABAB.xlsx...")
    total = len(pd_frame)
    
    for i in range(total):
        jp_words = pd_frame.iloc[i]["副词"]
        meaning = pd_frame.iloc[i]["意思"]
        findic[jp_words] = meaning
        if i % 100 == 0 or i == total - 1: # 优化网页渲染性能
            progress_bar.progress((i + 1) / total, text=f"正在处理 ABAB.xlsx... ({i+1}/{total})")
            
    progress_bar.empty() # 处理完清空进度条
    return findic

# ... (for_csv, for_grammar 等函数可参照 for_xlsx 的更改方式：传入 findic，替换 tqdm 为 st.progress，并加入文件是否存在的判断 os.path.exists) ...

def merge(findic):
    filenme = os.listdir(os.path.dirname(__file__))
    for i in filenme:
        if i.endswith(".json") and i != "final.json":
            with open(i, encoding="utf-8") as f:
                findic.update(json.load(f))
    return findic

# 【更改 4】：将原 for_anki.py 的逻辑封装为一个函数
def generate_anki_text(findic):
    out = []
    for word, meaning in findic.items():
        out.append("\t".join([str(word), str(meaning)]))
    return "\n".join(out)

# 【更改 5】：重写执行入口，构建 Streamlit UI 面板
def main():
    st.title("📚 日语词典构建工具")
    st.write("扫描当前仓库下的词典文件并合并为 JSON 与 Anki 导入格式。")

    if st.button("开始构建词典", type="primary"):
        findic = {} # 初始化字典
        
        with st.status("正在扫描和处理文件...", expanded=True) as status:
            # 您可以根据实际需要，取消注释您想要运行的处理模块
            # st.write("处理 Excel 文件...")
            # findic = for_xlsx(findic)
            
            st.write("合并所有 JSON 文件...")
            findic = merge(findic)
            
            status.update(label="处理完成！", state="complete", expanded=False)
            
        st.success(f"✅ 成功合并了 {len(findic)} 个词条！")
        
        # 将结果转为字符串供下载
        final_json_str = json.dumps(findic, indent=2, sort_keys=True, ensure_ascii=False)
        final_txt_str = generate_anki_text(findic)
        
        # 【更改 6】：提供 Streamlit 下载按钮，无需直接写入服务器磁盘
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 下载 final.json",
                data=final_json_str,
                file_name="final.json",
                mime="application/json"
            )
        with col2:
            st.download_button(
                label="📥 下载 final.txt (Anki专用)",
                data=final_txt_str,
                file_name="final.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
