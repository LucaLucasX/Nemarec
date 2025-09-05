import base64
import hashlib
import hmac
import io
import json
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request, send_file, render_template, Response
from flask_cors import CORS
from flask import send_file, send_from_directory
import os
from flask import make_response
from secrets import token_hex
from flask_socketio import SocketIO, emit
import threading

from zhipuai import ZhipuAI

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

app = Flask(__name__)
CORS(app,supports_credentials=True)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    print("保存路径：", save_path)
    file.save(save_path)
    file.close()
    relative_path = f"/static/uploads/{file.filename}"
    result = predict(save_path)

    return {
        'success': True,
        'data': [result, relative_path],
        'msg': 'success'
    }


@app.route('/download//<string:file_name>', methods=['GET'])
def download(file_name):
    return send_file(f"{file_name}")


# attachment_filename=file_name


def transform_image(image_bytes):
    transform = transforms.Compose([transforms.Resize((224, 224)),
                                    transforms.Grayscale(num_output_channels=3),
                                    transforms.ToTensor()])
    image = Image.open(io.BytesIO(image_bytes))
    return transform(image).unsqueeze(0)


def get_model():
    global model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = models.resnet101(pretrained=False)
    model.fc = nn.Linear(2048, 19)
    pthfile = 'resnet101_data_expansion_3x_best_model_parameters.pt'
    model_PT = torch.load(pthfile, map_location=device)
    model.load_state_dict(model_PT["model_state_dict"])
    model.eval()  # necessary to add brackets
    print('the model is loaded')


get_model()

# class_mapping = ('Helicotylenchus','Xenocriconema','Mylonchulus','Ditylenchus','Panagrolaimus','Rhbiditis','Pratylenchus','Acrobeloides','Pristionchus','Aphelenchoides','Axonchium','Aporcelaimus','Discolimus','Eudorylaimus','Mesodorylaimus','Miconchus','Dorylaimus','Amplimerlinius','Acrobeles')
class_mapping = (
    'Acrobeles', 'Acrobeloides', 'Amplimerlinius', 'Aphelenchoides', 'Aporcelaimus', 'Axonchium', 'Discolimus',
    'Ditylenchus', 'Dorylaimus', 'Eudorylaimus', 'Helicotylenchus', 'Mesodorylaimus', 'Miconchus', 'Mylonchulus',
    'Panagrolaimus', 'Pratylenchus', 'Pristionchus', 'Rhbiditis', 'Xenocriconema')


def get_category(image):
    file = open(image, 'rb')
    image_bytes = file.read()
    transformed_image = transform_image(image_bytes=image_bytes)
    outputs = model(transformed_image)
    _, category = torch.max(outputs, 1)
    predicted_idx = category.item()
    prob = F.softmax(outputs, dim=1)
    top_p, top_class = prob.topk(1, dim=1)
    category = {'class_name': class_mapping[predicted_idx], 'precentage': top_p.item()}
    print(category)
    return category


@app.route('/predict', methods=['POST'])
def predict(file):
    print(type(file))
    catg = get_category(image=file)
    print(catg)
    return catg

client = ZhipuAI(api_key="3490627a6b2940c7862f68b3773e5aab.zKaeZi38w15hqPue")  # 替换为你自己的 key

# 历史记录（简单起见放在全局变量中，生产环境建议基于 session 或数据库存储）
chat_history = [
    {"role": "system", "content": "你是一个专业的线虫专家助手，你的名字叫现小虫，你的任务是提供专业、准确、有洞察力的线虫相关建议。"
                                  "请不要回答用户未提问的问题"
                                  }
]

@app.route('/api', methods=['POST'])
def stream_response():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    image_url = data.get('image_url', '')
    if image_url:
        image_url = image_url.strip()

    if not user_input and not image_url:
        return "Missing 'user_input' or 'image_url'", 400

    # 组装当前轮的 message 内容（支持图文混合）
    current_content = []
    if image_url:
        current_content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url  # 公网地址，OpenAI/Zhipu等模型才能访问
            }
        })
    if user_input:
        current_content.append({
            "type": "text",
            "text": user_input
        })

    # 添加当前用户消息到聊天历史中（关键：不要清 chat_history）
    chat_history.append({"role": "user", "content": current_content})

    def generate():
        try:
            # 与模型接口通信（支持流式响应）
            response = client.chat.completions.create(
                model="glm-4v-flash",
                messages=chat_history,
                stream=True
            )

            assistant_reply = ""
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    assistant_reply += delta.content
                    yield f"data: {delta.content}\n\n"

            # 模型返回后将回复也加入历史
            chat_history.append({
                "role": "assistant",
                "content": [{"type": "text", "text": assistant_reply}]
            })

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [出错：{str(e)}]\n\n"

    return Response(generate(), content_type='text/event-stream')
@app.route('/clear-history', methods=['POST'])
def clear_history():
    global chat_history
    # 重置为初始状态
    chat_history = [
        {"role": "system", "content": "你是一个专业的线虫专家助手，你的名字叫现小虫，你的任务是提供专业、准确、有洞察力的线虫相关建议。请不要回答用户未提问的问题"}
    ]
    return jsonify({"status": "success"})

import oss2
from flask import request, jsonify

@app.route('/upload-to-oss', methods=['POST'])
def upload_to_oss():
    file = request.files.get('file')
    filename = request.form.get('filename', file.filename)

    access_key_id = "YOUR_ID"
    access_key_secret = "YOUR_KEY"
    bucket_name = "web-cure"
    endpoint = "oss-cn-guangzhou.aliyuncs.com"
    dir_prefix = "nemarec/"

    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    oss_path = dir_prefix + filename
    bucket.put_object(oss_path, file.read())

    oss_url = f"https://{bucket_name}.{endpoint}/{oss_path}"
    print(oss_url)
    return jsonify({"url": oss_url})


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=5000,debug=True)
