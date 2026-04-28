import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 获取当前脚本 (main.py) 所在的绝对路径
# 这样在 GitHub Cloud 运行的时候，它能精准定位到同文件夹下的词典文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 定义词典文件映射
DICTIONARY_MAP = {
    "日语 ➔ 中文": "small_kaikki.org-dictionary-日语.jsonl",
    "西班牙语 ➔ 中文": "small_kaikki.org-dictionary-西班牙语.jsonl",
    "日语 ➔ 韩语": "small_kaikki.org-dictionary-일본어.jsonl",
    "西班牙语 ➔ 韩语": "small_kaikki.org-dictionary-스페인어.jsonl",
    "中文 ➔ 韩语": "small_kaikki.org-dictionary-중국어.jsonl"
}

# 3. 侧边栏：语言切换器
st.sidebar.title("🌍 语言设置")
selected_lang = st.sidebar.selectbox("选择目标语言对", list(DICTIONARY_MAP.keys()))
file_name = DICTIONARY_MAP[selected_lang]

# 4. 加载数据的函数
@st.cache_data
def load_data(name):
    # 🌟 关键点：拼接绝对路径
    full_path = os.path.join(BASE_DIR, name)
    
    if not os.path.exists(full_path):
        return None
    
    data = []
    # 使用 utf-8 编码读取 jsonl
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return data

# 5. 主界面逻辑
st.title(f"📖 {selected_lang} 学习词典")

with st.spinner(f"正在从云端加载 {selected_lang} 数据..."):
    words_data = load_data(file_name)

if words_data is None:
    st.error(f"❌ 云端未找到文件: `{file_name}`。请确认该文件已上传到 GitHub 仓库根目录。")
else:
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
            
            # 搜索逻辑
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
