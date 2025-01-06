from functools import partial
import litellm
import base64

def image_to_dataurl(data,type="png"):
    # 对PNG字节进行base64编码
    encoded_png = base64.b64encode(data).decode('utf-8')
    # 创建data URL
    data_url = f"data:image/{type};base64,{encoded_png}"
    return data_url

def make_llm(**kwargs):
    assert "message" not in kwargs
    return partial(litellm.completion,**kwargs)

llm=make_llm(base_url="https://open.bigmodel.cn/api/paas/v4/",model="openai/glm-4v",api_key="19003893b371a8faeb6f09bbba97e037.4gjxGFg7x5o8KqpU")

data=image_to_dataurl(open("./image.png","rb").read(),"jpg")
response = llm(
    tempurate=0.5,
    messages=[
        {"role":"system","content":"""You are a helpful assistant who always return user with markdown"

        """},
        {
            "role": "user",
            "content": [
                            {
                                "type": "text",
                                "text": """将图片内容转为Markdown文档，使用"+++\{标题\}+++"代替文件中的标题
        """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": data
                                }
                            }
                        ]
        }
    ],
)


print(response.choices[0].message.content)
#print(llm(messages=[{"content": "你好，你好吗？", "role": "user"}]))

