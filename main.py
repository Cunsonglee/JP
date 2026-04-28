import streamlit as st
import json

# 设置网页标题和图标
st.set_page_config(page_title="我的日语词典", page_icon="🏮")

# 加载词典数据的函数（增加缓存避免重复加载）
@st.cache_data
def load_dictionary():
    with open('dict.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['words']

# 界面展示
st.title("🎌 个人日语学习词典")
st.markdown("---")

# 获取数据
try:
    words = load_dictionary()
    
    # 搜索框
    query = st.text_input("输入你想查询的内容 (支持日语汉字、假名或中文):")

    if query:
        results = []
        # 遍历词典查找匹配项
        for entry in words:
            # 提取汉字、假名、和释义
            kanjis = [k['text'] for k in entry.get('kanji', [])]
            kanas = [r['text'] for r in entry.get('kana', [])]
            # 找到中文释义 (zho)
            definitions = []
            for s in entry.get('sense', []):
                for g in s.get('gloss', []):
                    # 只有当释义是中文时才加入
                    definitions.append(g['text'])
            
            all_text = "".join(kanjis) + "".join(kanas) + "".join(definitions)
            
            # 如果搜索词在任何一个字段里
            if query.lower() in all_text.lower():
                results.append({
                    "word": kanjis[0] if kanjis else kanas[0],
                    "reading": " | ".join(kanas),
                    "meanings": definitions
                })
            
            # 限制显示前 20 条，防止网页卡死
            if len(results) >= 20:
                break

        # 显示结果
        if results:
            for r in results:
                with st.expander(f"✨ {r['word']} ({r['reading']})"):
                    for idx, m in enumerate(r['meanings']):
                        st.write(f"{idx+1}. {m}")
        else:
            st.warning("没找到这个词，换个试试？")

except FileNotFoundError:
    st.error("找不到 dict.json 文件，请确保文件放在项目文件夹中！")
