import gradio as gr
from functools import partial
import litellm
import base64
import io
from PIL import Image
import zipfile
def image_to_dataurl(data, file_type="png"):
    encoded = base64.b64encode(data).decode('utf-8')
    return f"data:image/{file_type};base64,{encoded}"

def make_llm(**kwargs):
    assert "message" not in kwargs
    return partial(litellm.completion, **kwargs)

llm = make_llm(
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    model="openai/glm-4v",
    api_key="19003893b371a8faeb6f09bbba97e037.4gjxGFg7x5o8KqpU"
)

def generate_markdown(uploaded_image):
    if uploaded_image is None:
        return "No image uploaded."
    buffered = io.BytesIO()
    uploaded_image.save(buffered, format="PNG")
    data_bytes = buffered.getvalue()
    data_url = image_to_dataurl(data_bytes, "png")
    response = llm(
        tempurate=0.5,
        messages=[
            {"role": "system", 
             "content": "You are a helpful assistant who always return user with markdown"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """将图片内容转为Markdown文档，使用"+++\{标题\}+++"代替文件中的标题
                                   使用
                                """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    }
                ]
            }
        ],
    )
    return response.choices[0].message.content,

with gr.Blocks() as demo:
    gr.Markdown("## 上传PNG图片转Markdown")
    with gr.Row():
        with gr.Column():
            img_input = gr.Image(type="pil", label="上传PNG图片")
            generate_btn = gr.Button("Generate Markdown")
        with gr.Column():
            md_output = gr.Markdown()
            downloader= gr.File()
    generate_btn.click(fn=generate_markdown, inputs=img_input, outputs=md_output)

demo.launch()