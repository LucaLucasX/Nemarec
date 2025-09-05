from zhipuai import ZhipuAI

client = ZhipuAI(api_key="3490627a6b2940c7862f68b3773e5aab.zKaeZi38w15hqPue")  # 替换为你自己的 key

def main():
    print("💬 欢迎使用 ZhipuAI 对话系统，输入 'exit' 退出。\n")

    history = [
        {"role": "system", "content": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。"},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": r"https://web-cure.oss-cn-guangzhou.aliyuncs.com/26d97d17-2713-4c8f-b639-9dc8bd4d2a25.jpg"
                    }
                },
            ]
        },
    ]

    while True:
        user_input = input("\n👤 你：")
        if user_input.strip().lower() in ["exit", "quit", "退出"]:
            print("👋 再见！")
            break

        history.append({"role": "user", "content": user_input})

        print("🤖 AI：", end="", flush=True)

        try:
            response = client.chat.completions.create(
                model="glm-4v-flash",
                messages=history,
                stream=True
            )

            reply = ""
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    reply += delta.content
                    print(delta.content, end="", flush=True)

            history.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"\n❌ 出错：{e}")

if __name__ == "__main__":
    main()
