# AI toolkits

1. Put environment variables in home directory, `~/.env`

```
OPENAI_API_KEY="your_openai_api_key"
AZURE_OPENAI_API_KEY="your azure_openai_api_key"
AZURE_OPENAI_ENDPOINT="your azure_openai_endpoint"
```


2. Install project
```
pip install .
```

3. 同声传译（输入语音，输出文本）
```bash
❯ gotalk translate
```

```bash
Preparing to start...
Start speaking now...
Translation: Ah, what day is it today?
Translation: What day is it tomorrow?
Translation: What will the weather be like tomorrow?
```


4. 聊天应用（输入语音，输出文本）
```bash
gotalk chat --duration 300
```

```bash
Preparing to start...
Start speaking now...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                 🟦 Turn 1 🟦                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

😏 User: 你好。
🤖 Assistant: 你好！有什么我可以帮你的吗？

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                 🟦 Turn 2 🟦                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

😏 User: 叫什么名字？
🤖 Assistant: 我是你的AI助手，还没有自己的名字哦。如果你想，可以帮我起一个名字！
```