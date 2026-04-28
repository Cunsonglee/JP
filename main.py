import streamlit as st
import json
import os

# 1. 页面基本配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 🌟 核心修复：锁定 main.py 所在的真实文件夹
# 无论文件在哪个子文件夹，这段代码都能帮程序定位到它身边的词典
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 词典文件映射
DICTIONARY_MAP = {
    "日语 ➔ 中文": "small_kaikki.org-dictionary-日语.jsonl",
    "西班牙语 ➔ 中文": "small_kaikki.org-dictionary-西班牙语.jsonl",
    "日语 ➔ 韩语": "small_kaikki.org-dictionary-일본어.jsonl",
    "西班牙语 ➔ 韩语": "small_kaikki.org-dictionary-스페인어.jsonl",
    "中文 ➔ 韩语": "small_kaikki.org-dictionary-중국어.jsonl"
}

# 3. 侧边栏：语言设置
st.sidebar.title("🌍 语言设置")
selected_lang = st.sidebar.selectbox("选择目标语言对", list(DICTIONARY_MAP.keys()))
target_file_name = DICTIONARY_MAP[selected_lang]

# 4. 加载数据的函数
@st.cache_data
def load_data(file_name):
    # 🌟 修复关键：使用 BASE_DIR 拼接绝对路径
    full_path = os.path.join(BASE_DIR, file_name)
    
    if not os.path.exists(full_path):
        return None
    
    data = []
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except:
                        continue
        return data
    except Exception as e:
        st.error(f"读取文件出错: {e}")
        return None

# 5. 主界面逻辑
st.title(f"📖 {selected_lang} 学习词典")

# 尝试加载数据
words_data = load_data(target_file_name)

if words_data is None:
    # 🌟 诊断模式：如果找不到文件，列出代码所在文件夹的文件列表
    st.error(f"❌ 找不到文件: `{target_file_name}`")
    st.write("--- 自动诊断信息 ---")
    st.write(f"当前代码所在路径: `{BASE_DIR}`")
    st.write("该文件夹下的文件列表：")
    try:
        st.write(os.listdir(BASE_DIR))
    except:
        st.write("无法读取文件夹列表")
else:
    # 搜索逻辑
    query = st.text_input(f"在 {selected_lang} 中搜索：", placeholder="输入单词或含义...")

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
