import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

st.set_page_config(page_title="高级批量水印工具", layout="wide")
st.title("🛠️ 云端批量水印工厂")

# --- 侧边栏设置 ---
st.sidebar.header("水印配置")
alpha = st.sidebar.slider("不透明度", 0, 255, 128)
pos_x = st.sidebar.number_input("位置 X", value=50)
pos_y = st.sidebar.number_input("位置 Y", value=50)

wm_text = st.sidebar.text_input("水印文字", "我的专属水印")
font_size = st.sidebar.slider("文字大小", 10, 200, 50)

logo_file = st.sidebar.file_uploader("上传 Logo (可选)", type=['png', 'jpg'])

# --- 主界面 ---
uploaded_files = st.file_uploader("上传图片 (支持多选)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    # 准备一个内存里的压缩包
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGBA")
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 加文字
            try:
                # 云端服务器通用字体
                font = ImageFont.load_default() 
            except:
                font = None
            draw.text((pos_x, pos_y), wm_text, fill=(255, 255, 255, alpha), font=font)
            
            # 加 Logo
            if logo_file:
                logo = Image.open(logo_file).convert("RGBA")
                # 简单缩放
                logo.thumbnail((200, 200))
                overlay.paste(logo, (pos_x, pos_y + font_size), logo)
            
            out = Image.alpha_composite(img, overlay).convert("RGB")
            
            # 保存到内存
            img_byte_arr = io.BytesIO()
            out.save(img_byte_arr, format='JPEG')
            zip_file.writestr(f"watermarked_{file.name}", img_byte_arr.getvalue())
            
            if idx == 0:
                st.image(out, caption="预览第一张效果", use_container_width=True)

    st.success(f"✅ 已处理 {len(uploaded_files)} 张图片")
    
    # 下载按钮
    st.download_button(
        label="📥 点击下载所有水印图片 (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="watermarked_images.zip",
        mime="application/zip"
    )
