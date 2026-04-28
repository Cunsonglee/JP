import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        return None, "找不到文件"
    
    data = []
    try:
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except:
                    continue
        return data, None
    except Exception as e:
        return None, str(e)

st.title(f"📖 {selected_lang} 学习词典")

words_data, error_info = load_data(target_file_name)

if error_info == "找不到文件":
    st.error(f"❌ 找不到文件: `{target_file_name}`")
elif not words_data:
    st.warning("⚠️ 警告：无法识别里面的数据格式。")
else:
    query = st.text_input(f"在 {selected_lang} 中搜索：", placeholder="输入想查的单词...")
    
    if query:
        results = []
        q = query.lower()
        
        # 🌟 最安全的搜索逻辑，完全避免 NoneType 报错
        for w in words_data:
            # 安全获取 word
            word = w.get('word') or ''
            
            # 安全获取 senses，如果是 null (None) 就自动变成 []
            senses = w.get('senses') or []
            
            glosses = []
            for s in senses:
                # 安全获取 glosses，如果是 null (None) 就自动变成 []
                g_list = s.get('glosses') or []
                glosses.extend(g_list)
            
            # 搜索判断
            if q in word.lower() or any(q in str(g).lower() for g in glosses):
                results.append({
                    "word": word,
                    "pos": w.get('pos') or '未知',
                    "meanings": glosses
                })
            
            if len(results) >= 20: 
                break
        
        if results:
            for r in results:
                with st.expander(f"✨ {r['word']} [{r['pos']}]"):
                    for i, m in enumerate(r['meanings']):
                        st.write(f"{i+1}. {m}")
        else:
            st.info("没有找到匹配项。")
