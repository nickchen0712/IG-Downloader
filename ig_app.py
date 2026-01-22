import streamlit as st
import instaloader
import requests
import re
from io import BytesIO

st.set_page_config(page_title="IG 下載神器 (除錯版)", page_icon="🛠️")

st.title("🛠️ Instagram 下載器 - 除錯模式")
st.info("如果無法下載，請看下方的紅色錯誤訊息，它會告訴我們原因。")

L = instaloader.Instaloader()

url = st.text_input("🔗 請貼上 Instagram 貼文連結:", placeholder="https://www.instagram.com/p/xxxxx/")

if url:
    # --- 改良點 1: 更強的網址擷取 (不用擔心有沒有斜線) ---
    # 它的意思是：找 /p/ 後面那串字，直到遇到 '/' 或 '?' 為止
    shortcode_match = re.search(r'/p/([^/?]+)', url)
    
    if shortcode_match:
        shortcode = shortcode_match.group(1)
        st.write(f"正在嘗試讀取貼文代碼: `{shortcode}` ...") # 顯示目前抓到的 ID
        
        if st.button("🚀 開始抓取"):
            try:
                with st.spinner('正在連線到 Instagram...'):
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    
                    image_urls = []
                    if post.typename == 'GraphSidecar':
                        for node in post.get_sidecar_nodes():
                            if not node.is_video: 
                                image_urls.append(node.display_url)
                    elif post.typename == 'GraphImage':
                        image_urls.append(post.url)
                    else:
                        st.warning("⚠️ 這個連結似乎是影片，目前只能下載照片喔！")

                    if image_urls:
                        st.success(f"成功！找到 {len(image_urls)} 張照片")
                        for i, img_url in enumerate(image_urls):
                            # 使用 columns 讓版面好看一點
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(img_url, use_column_width=True)
                            with col2:
                                response = requests.get(img_url)
                                st.download_button(
                                    label=f"⬇️ 下載照片 {i+1}",
                                    data=BytesIO(response.content),
                                    file_name=f"ig_{shortcode}_{i+1}.jpg",
                                    mime="image/jpeg"
                                )
                                
            except Exception as e:
                # --- 改良點 2: 顯示真實的錯誤訊息 ---
                st.error("❌ 讀取失敗！")
                st.markdown(f"**系統回傳的錯誤原因 (請截圖這行):**\n```\n{e}\n```")
                
                # 幫你判斷常見錯誤
                error_msg = str(e).lower()
                if "login required" in error_msg or "redirected to login" in error_msg:
                    st.warning("💡 **原因分析**：Instagram 拒絕了匿名訪問。這通常發生在雲端主機 (Streamlit Cloud) 上，因為 IG 會封鎖資料中心的 IP。")
                    st.info("👉 **解決方法**：請改用電腦本機版 (在 Mac 終端機執行) 通常就能解決。")
                elif "404" in error_msg:
                    st.warning("💡 **原因分析**：找不到貼文。可能是連結貼錯，或是該帳號已轉為私人。")
    else:
        st.error("⚠️ 無法辨識連結格式，請確認網址裡有包含 `/p/`")