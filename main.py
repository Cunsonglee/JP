import streamlit as st
import json
import os

# 1. 页面配置
st.set_page_config(page_title="全球语通 - 多语言词典", page_icon="🌍", layout="wide")

# 获取当前文件的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 词典映射
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

# 3. 超强鲁棒性的加载函数
@st.cache_data
def load_data(file_name):
    full_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(full_path):
        return None, "找不到文件"
    
    data = []
    try:
        # 使用 utf-8-sig 自动处理隐藏的 BOM 字符
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # 尝试解析 JSON，失败则跳过这一行
                    data.append(json.loads(line))
                except:
                    continue
        return data, None
    except Exception as e:
        return None, str(e)

# 4. 主界面
st.title(f"📖 {selected_lang} 学习词典")

words_data, error_info = load_data(target_file_name)

if error_info == "找不到文件":
    st.error(f"❌ 找不到文件: `{target_file_name}`")
    st.write("当前文件夹文件列表:", os.listdir(BASE_DIR))
elif not words_data:
    # 🌟 这里是诊断模式
    st.warning("⚠️ 警告：文件已打开，但无法识别里面的数据格式。")
    # 尝试读出文件前 50 个字符看看到底是什么
    full_path = os.path.join(BASE_DIR, target_file_name)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            head = f.read(50)
            st.code(f"文件开头预览: {head}", language="text")
            st.info("如果上面显示的是 <!DOCTYPE 或 { \"payload\"，说明你上传的是 GitHub 的网页，而不是原始数据文件！")
else:
    # 5. 正常的搜索逻辑
    query = st.text_input(f"在 {selected_lang} 中搜索词汇：", placeholder="输入想查的单词...")
    
    if query:
        q = query.lower()
        results = [w for w in words_data if q in w.get('word', '').lower() or 
                  any(q in str(g).lower() for s in w.get('senses', []) for g in s.get('glosses', []))]
        
        if results:
            for r in results[:20]:
                with st.expander(f"✨ {r['word']} [{r['pos']}]"):
                    for i, s in enumerate(r.get('senses', [])):
                        glosses = s.get('glosses', [])
                        if glosses:
                            st.write(f"{i+1}. {', '.join(glosses)}")
        else:
            st.info("没有找到匹配项。")
