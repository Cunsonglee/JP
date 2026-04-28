import streamlit as st
import json
import os

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
        return None
    
    data = []
    # 🌟 修复1：使用 'utf-8-sig' 代替 'utf-8'，这能自动清除 Windows 偷偷加上的隐藏 BOM 字符
    try:
        with open(full_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if line.strip():
                    # 🌟 修复2：加上内层保护罩，哪怕某一行数据全坏了，代码也会跳过它，而不是让整个 App 崩溃
                    try:
                        data.append(json.loads(line))
                    except:
                        continue
        return data
    except Exception as e:
        return None

st.title(f"📖 {selected_lang} 学习词典")

words_data = load_data(target_file_name)

if words_data is None:
    st.error(f"❌ 找不到文件: `{target_file_name}`")
elif len(words_data) == 0:
    # 🌟 诊断3：如果没报错，但是数据是 0 条，说明文件里面装的不是字典代码！
    st.warning(f"⚠️ 成功读取了 `{target_file_name}`，但里面没有任何有效数据。")
    st.info("请在 GitHub 网页上点开这个文件，看看里面是不是写满了 `<!DOCTYPE html>` 这样的网页代码？如果是，说明你上传错文件了。它里面应该是 `{\"word\": \"...\"}` 这样的格式。")
else:
    query = st.text_input(f"在 {selected_lang} 中搜索：", placeholder="输入想查的单词或意思...")

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
