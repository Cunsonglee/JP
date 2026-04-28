import streamlit as st
import json
import os

# 1. 页面基本配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 🌟 关键修复：锁定当前 main.py 所在的文件夹路径
# 不管是在你电脑还是在 Streamlit 云端，这段代码都能帮程序精准定位文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 词典文件映射 (请确保你的 GitHub 仓库根目录下确实有这些 small_ 开头的文件)
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
# 获取对应的文件名
target_file_name = DICTIONARY_MAP[selected_lang]

# 4. 加载数据的函数
@st.cache_data
def load_data(file_name):
    # 🌟 关键修复：拼接成绝对路径
    full_path = os.path.join(BASE_DIR, file_name)
    
    if not os.path.exists(full_path):
        return None
    
    data = []
    # 增加 encoding='utf-8' 确保中文/韩文不乱码
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return data

# 5. 主界面逻辑
st.title(f"📖 {selected_lang} 学习词典")

# 加载数据
with st.spinner(f"正在从云端加载 {selected_lang} 数据..."):
    words_data = load_data(target_file_name)

if words_data is None:
    # 如果还是找不到，显示详细的调试信息，方便我们排查
    st.error(f"❌ 错误：在云端文件夹中找不到文件 `{target_file_name}`")
    st.info(f"请检查你的 GitHub 仓库，确认该文件确实存在于根目录下，且名字完全一致。")
else:
    # 搜索框
    query = st.text_input(f"输入搜索词 (支持日语、西语或中文含义):", placeholder="例如: 日本 / Hola / 学习")

    if query:
        results = []
        q = query.lower()
        for entry in words_data:
            word = entry.get('word', '')
            senses = entry.get('senses', [])
            
            # 提取所有释义
            glosses = []
            for s in senses:
                glosses.extend(s.get('glosses', []))
            
            # 搜索匹配逻辑
            if q in word.lower() or any(q in g.lower() for g in glosses):
                results.append({
                    "word": word,
                    "pos": entry.get('pos', '词性未知'),
                    "meanings": glosses
                })
            
            if len(results) >= 20: break # 限制显示前20个

        # 展示搜索结果
        if results:
            st.write(f"找到 {len(results)} 条相关结果：")
            for r in results:
                with st.expander(f"✨ {r['word']} [{r['pos']}]"):
                    for idx, m in enumerate(r['meanings']):
                        st.write(f"{idx+1}. {m}")
        else:
            st.warning("没有找到匹配的单词，请尝试输入其他关键词。")
