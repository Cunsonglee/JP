import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 获取 main.py 所在的文件夹路径（根目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 词典文件映射
DICTIONARY_MAP = {
    "日语 ➔ 中文": "small_kaikki.org-dictionary-日语.jsonl",
    "西班牙语 ➔ 中文": "small_kaikki.org-dictionary-西班牙语.jsonl",
    "日语 ➔ 韩语": "small_kaikki.org-dictionary-일본어.jsonl",
    "西班牙语 ➔ 韩语": "small_kaikki.org-dictionary-스페인어.jsonl",
    "中文 ➔ 韩语": "small_kaikki.org-dictionary-중국어.jsonl"
}

st.sidebar.title("🌍 语言设置")
selected_lang = st.sidebar.selectbox("选择目标语言对", list(DICTIONARY_MAP.keys()))
target_file_name = DICTIONARY_MAP[selected_lang]

@st.cache_data
def load_data(file_name):
    full_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(full_path):
        return None, f"找不到文件: {full_path}"
    
    data = []
    try:
        # 使用 'utf-8-sig' 处理可能存在的 BOM 字符
        with open(full_path, 'r', encoding='utf-8-sig') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    # 如果第一行就报错，可能是因为文件内容变成了 HTML 网页代码
                    if line_num == 1 and line.startswith('<'):
                        return None, "错误：文件内容似乎是网页(HTML)而不是数据。请重新上传原始数据文件。"
                    continue # 忽略其他错误的行
        return data, None
    except Exception as e:
        return None, str(e)

st.title(f"📖 {selected_lang} 学习词典")

words_data, error_msg = load_data(target_file_name)

if error_msg:
    st.error(f"❌ 加载失败: {error_msg}")
    # 辅助诊断：看看文件前 100 个字符到底是什么
    full_path = os.path.join(BASE_DIR, target_file_name)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            head = f.read(100)
            st.write("文件开头预览（诊断用）:", head)
elif not words_data:
    st.warning("⚠️ 文件为空或格式完全不匹配。")
else:
    query = st.text_input(f"在 {selected_lang} 中搜索：", placeholder="输入想查的单词或含义...")

    if query:
        results = []
        q = query.lower()
        for entry in words_data:
            word = entry.get('word', '')
            senses = entry.get('senses', [])
            glosses = []
            for s in senses:
                glosses.extend(s.get('glosses', []))
            
            if q in word.lower() or any(q in g.lower() for g in glosses):
                results.append({
                    "word": word,
                    "pos": entry.get('pos', 'N/A'),
                    "meanings": glosses
                })
            
            if len(results) >= 20: break

        if results:
            for r in results:
                with st.expander(f"✨ {r['word']} [{r['pos']}]"):
                    for idx, m in enumerate(r['meanings']):
                        st.write(f"{idx+1}. {m}")
        else:
            st.info("没有找到匹配项。")
