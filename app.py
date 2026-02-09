import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="可视化拖拽水印", layout="wide")
st.title("🖱️ 鼠标拖拽定位水印工厂")

# --- 侧边栏设置 ---
st.sidebar.header("配置区")
wm_text = st.sidebar.text_input("水印文字", "我的专属水印")
font_size = st.sidebar.slider("字体大小", 10, 150, 40)
alpha = st.sidebar.slider("透明度", 0, 255, 150)
text_color = st.sidebar.color_picker("文字颜色", "#FFFFFF")

uploaded_files = st.file_uploader("上传图片", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    # 加载第一张图作为底图
    bg_image = Image.open(uploaded_files[0])
    w, h = bg_image.size
    
    # 为了方便在网页操作，如果图片太大，我们按比例缩小显示
    max_display_width = 800
    display_ratio = max_display_width / w
    display_h = int(h * display_ratio)

    st.write("💡 **操作指南：** 点击左侧工具栏的 [选择箭头]，即可拖动水印文字。")

    # --- 创建交互式画布 ---
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # 填充透明
        stroke_width=1,
        background_image=bg_image,
        update_streamlit=True,
        height=display_h,
        width=max_display_width,
        drawing_mode="transform", # 设置为变换模式，允许拖动
        initial_drawing={
            "objects": [{
                "type": "text",
                "left": 50,
                "top": 50,
                "text": wm_text,
                "fontSize": font_size,
                "fill": text_color,
                "opacity": alpha / 255
            }]
        },
        key="canvas",
    )

    # --- 获取拖拽后的位置 ---
    final_x, final_y = 50, 50 # 默认值
    if canvas_result.json_data and "objects" in canvas_result.json_data:
        if len(canvas_result.json_data["objects"]) > 0:
            obj = canvas_result.json_data["objects"][0]
            # 还原回原图比例的坐标
            final_x = int(obj["left"] / display_ratio)
            final_y = int(obj["top"] / display_ratio)

    # --- 批量处理按钮 ---
    if st.button("🚀 确认当前位置，开始批量导出"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            progress_bar = st.progress(0)
            for i, file in enumerate(uploaded_files):
                img = Image.open(file).convert("RGBA")
                txt_layer = Image.new("RGBA", img.size, (0,0,0,0))
                draw = ImageDraw.Draw(txt_layer)
                
                # 绘制最终位置的水印
                draw.text((final_x, final_y), wm_text, fill=(255, 255, 255, alpha))
                
                out = Image.alpha_composite(img, txt_layer).convert("RGB")
                
                # 存入压缩包
                img_byte_arr = io.BytesIO()
                out.save(img_byte_arr, format='JPEG')
                zip_file.writestr(f"output_{file.name}", img_byte_arr.getvalue())
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.success("全部处理完成！")
        st.download_button("📥 点击下载 ZIP 压缩包", zip_buffer.getvalue(), "batch_watermark.zip")
