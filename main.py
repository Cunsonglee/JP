import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 🌟 关键修复：获取当前 main.py 所在的绝对路径
# 这行代码保证了无论在谁的电脑或哪个服务器上，都能精准定位
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 定义词典文件映射 (请确保文件名与仓库中的完全一致)
DICTIONARY_MAP = {
    "日语 ➔ 中文": "small_kaikki.org-dictionary-日语.jsonl",
    "西班牙语 ➔ 中文": "small_kaikki.org-dictionary-西班牙语.jsonl",
    "日语 ➔ 韩语": "small_kaikki.org-dictionary-일본어.jsonl",
    "西班牙语 ➔ 韩语": "small_kaikki.org-dictionary-스페인어.jsonl",
    "中文 ➔ 韩语": "small_kaikki.org-dictionary-중국어.jsonl"
}

# 3. 侧边栏设置
st.sidebar.title("🌍 语言设置")
selected_lang = st.sidebar.selectbox("选择目标语言对", list(DICTIONARY_MAP.keys()))
current_file_name = DICTIONARY_MAP[selected_lang]

# 4. 加载数据的函数
@st.cache_data
def load_data(file_name):
    # 🌟 关键修复：使用绝对路径拼接
    full_path = os.path.join(BASE_DIR, file_name)
    
    if not os.path.exists(full_path):
        return None
    
    data = []
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return data

# 5. 主界面逻辑
st.title(f"📖 {selected_lang} 学习词典")

with st.spinner(f"正在加载 {selected_lang} 数据..."):
    words_data = load_data(current_file_name)

if words_data is None:
    st.error(f"❌ 找不到文件: `{current_file_name}`")
    # 诊断信息：帮助我们看到服务器到底在哪个路径找文件
    st.info(f"程序尝试寻找的完整路径是: `{os.path.join(BASE_DIR, current_file_name)}`")
    st.write("当前目录下的文件列表:", os.listdir(BASE_DIR))
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
