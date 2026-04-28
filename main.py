import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 2. 定义词典文件映射 (确保文件名和你文件夹里的一模一样)
DICTIONARY_MAP = {
    "日语 ➔ 中文": "kaikki.org-dictionary-日语.jsonl",
    "西班牙语 ➔ 中文": "kaikki.org-dictionary-西班牙语.jsonl",
    "日语 ➔ 韩语": "kaikki.org-dictionary-일본어.jsonl",
    "西班牙语 ➔ 韩语": "kaikki.org-dictionary-스페인어.jsonl",
    "中文 ➔ 韩语": "kaikki.org-dictionary-중국어.jsonl"
}

# 3. 侧边栏：语言切换器
st.sidebar.title("🌍 语言设置")
selected_lang = st.sidebar.selectbox("选择目标语言对", list(DICTIONARY_MAP.keys()))
current_file = DICTIONARY_MAP[selected_lang]

# 4. 加载数据的函数（增加缓存）
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# 5. 主界面逻辑
st.title(f"📖 {selected_lang} 学习词典")

# 加载数据
with st.spinner(f"正在准备 {selected_lang} 数据..."):
    words_data = load_data(current_file)

if words_data is None:
    st.error(f"未找到文件: `{current_file}`。请确保它在项目根目录下。")
else:
    # 搜索框
    query = st.text_input(f"在 {selected_lang} 中搜索：", placeholder="输入单词或含义...")

    if query:
        results = []
        for entry in words_data:
            word = entry.get('word', '')
            # 提取所有释义
            senses = entry.get('senses', [])
            glosses = []
            for s in senses:
                glosses.extend(s.get('glosses', []))
            
            # 搜索逻辑：匹配单词本身或含义
            if query.lower() in word.lower() or any(query.lower() in g.lower() for g in glosses):
                results.append({
                    "word": word,
                    "pos": entry.get('pos', 'N/A'),
                    "meanings": glosses,
                    "sounds": entry.get('sounds', [])
                })
            
            if len(results) >= 20: break # 限制显示数量

        # 展示结果
        if results:
            for r in results:
                with st.expander(f"✨ {r['word']} [{r['pos']}]"):
                    # 如果有发音或音频信息
                    if r['sounds']:
                        st.write("**发音/音频信息:**")
                        for s in r['sounds']:
                            if 'ipa' in s: st.text(f"IPA: {s['ipa']}")
                            if 'text' in s: st.text(f"说明: {s['text']}")
                    
                    st.write("**基本释义:**")
                    for i, m in enumerate(r['meanings']):
                        st.write(f"{i+1}. {m}")
        else:
            st.info("没有找到匹配项。")
