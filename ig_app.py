import streamlit as st
import instaloader
import requests
import re
from io import BytesIO

# 設定網頁標題
st.set_page_config(page_title="IG 下載神器", page_icon="📸")

# 標題區
st.title("📸 Instagram 照片下載器")
st.markdown("只要貼上 **公開帳號** 的貼文連結，就能一鍵下載照片！")

# 初始化 Instaloader
L = instaloader.Instaloader()

# 輸入區
url = st.text_input("🔗 請貼上 Instagram 貼文連結:", placeholder="例如：https://www.instagram.com/p/CwPd1...")

if url:
    # 嘗試從連結中抓取 Shortcode
    shortcode_match = re.search(r'/p/([^/]+)/', url)
    
    if shortcode_match:
        shortcode = shortcode_match.group(1)
        
        if st.button("🚀 開始抓取"):
            try:
                with st.spinner('正在連線到 Instagram...'):
                    # 獲取貼文資訊
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    
                    image_urls = []
                    
                    # 判斷是多圖 (Sidecar) 還是單圖
                    if post.typename == 'GraphSidecar':
                        for node in post.get_sidecar_nodes():
                            if not node.is_video: 
                                image_urls.append(node.display_url)
                    elif post.typename == 'GraphImage':
                        image_urls.append(post.url)
                    else:
                        st.warning("⚠️ 這個連結似乎是影片，目前只能下載照片喔！")

                    # 顯示結果
                    if image_urls:
                        st.success(f"成功找到 {len(image_urls)} 張照片！")
                        st.divider() # 分隔線
                        
                        # 顯示每一張圖與下載按鈕
                        for i, img_url in enumerate(image_urls):
                            col1, col2 = st.columns([2, 1]) # 切分版面：左邊顯示圖，右邊顯示按鈕
                            
                            # 抓取圖片資料
                            response = requests.get(img_url)
                            img_bytes = BytesIO(response.content)
                            
                            with col1:
                                st.image(img_url, use_column_width=True)
                            with col2:
                                st.write(f"**照片 #{i+1}**")
                                st.download_button(
                                    label=f"⬇️ 下載此照片",
                                    data=img_bytes,
                                    file_name=f"ig_photo_{shortcode}_{i+1}.jpg",
                                    mime="image/jpeg"
                                )
                                st.write("") # 空行
            except Exception as e:
                st.error("❌ 無法讀取貼文，請確認：\n1. 帳號是**公開**的\n2. 連結沒有貼錯")
    else:
        st.info("💡 連結格式看起來不太對，應該要有 '/p/' 喔")