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
![Chat application screenshot](images/chat.png)

*Figure: Chat application output.*
