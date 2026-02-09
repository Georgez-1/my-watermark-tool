import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="交互式批量水印工具", layout="wide")
st.title("🎯 精准定位水印工厂")

# --- 初始化位置 (如果没点击过，默认在 50, 50) ---
if "coords" not in st.session_state:
    st.session_state.coords = {"x": 50, "y": 50}

# --- 侧边栏设置 ---
st.sidebar.header("配置区")
alpha = st.sidebar.slider("透明度", 0, 255, 150)
wm_text = st.sidebar.text_input("水印文字", "点击图片调整位置")
font_size = st.sidebar.slider("文字大小", 10, 200, 50)
logo_file = st.sidebar.file_uploader("上传 Logo (可选)", type=['png', 'jpg', 'jpeg'])

# --- 主界面 ---
uploaded_files = st.file_uploader("上传图片 (支持多选)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    # 1. 基础图片处理
    base_img = Image.open(uploaded_files[0]).convert("RGBA")
    
    st.write("💡 **直接点击下方预览图，水印会自动移动到点击处：**")
    
    # 2. 获取点击坐标
    # 我们先渲染一张带水印的预览图
    def render_preview(img, x, y):
        overlay = Image.new("RGBA", img.size, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)
        draw.text((x, y), wm_text, fill=(255, 255, 255, alpha))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((200, 200))
            overlay.paste(logo, (int(x), int(y + font_size)), logo)
        return Image.alpha_composite(img, overlay).convert("RGB")

    # 展示可点击的预览图
    value = streamlit_image_coordinates(render_preview(base_img, st.session_state.coords["x"], st.session_state.coords["y"]))

    # 如果用户点击了图片，更新坐标并刷新
    if value:
        st.session_state.coords["x"] = value["x"]
        st.session_state.coords["y"] = value["y"]
        st.rerun()

    st.write(f"当前位置：X={st.session_state.coords['x']}, Y={st.session_state.coords['y']}")

    # 3. 批量处理与下载
    if st.button("🚀 确认位置并批量打包下载"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for file in uploaded_files:
                img = Image.open(file).convert("RGBA")
                overlay = Image.new("RGBA", img.size, (0,0,0,0))
                draw = ImageDraw.Draw(overlay)
                draw.text((st.session_state.coords["x"], st.session_state.coords["y"]), wm_text, fill=(255, 255, 255, alpha))
                # ... Logo 逻辑同上 ...
                out = Image.alpha_composite(img, overlay).convert("RGB")
                
                img_byte_arr = io.BytesIO()
                out.save(img_byte_arr, format='JPEG')
                zip_file.writestr(f"wm_{file.name}", img_byte_arr.getvalue())
        
        st.download_button("📥 点击下载 ZIP 包", zip_buffer.getvalue(), "watermarked.zip", "application/zip")
