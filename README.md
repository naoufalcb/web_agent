---
title: Web Agent
emoji: 🌐
colorFrom: blue
colorTo: yellow
sdk: gradio
sdk_version: 5.23.1
app_file: app.py
pinned: false
tags:
- smolagents
- agent
- smolagent
---
# Web Search Agent

A powerful AI-powered web agent that can search the web, summarize webpages, and provide time information across different timezones.

## 🚀 Demo

Try out the live demo on Hugging Face Spaces:  
## [👉 View Demo Here 🎈](https://huggingface.co/spaces/naoufalcb/web_agent)

## ✨ Features

- 🔍 Web Search: Search the internet using DuckDuckGo
- 📝 Webpage Summarization: Get concise summaries of web content
- 🕒 Timezone Information: Get current time in any timezone
- 🤖 AI-Powered Responses: Using Azure's LLama model for intelligent interactions
- 🖥️ User-Friendly Interface: Built with Gradio for easy interaction

## 🛠️ Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and add your Azure API credentials:
```env
AZURE_ENDPOINT=your_endpoint
AZURE_API_KEY=your_api_key
```

## 🚦 Usage

Run the application:
```bash
python app.py
```

The web interface will be available at `http://localhost:7860`

## 🔧 Tools Available

The agent comes with several built-in tools:

1. **Web Search**: Search the internet using DuckDuckGo
2. **Webpage Summarizer**: Get summaries of web content
3. **Timezone Tool**: Get current time in any timezone
4. **Final Answer Tool**: Provides conclusive responses to queries

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🔗 References

- Built with [Gradio](https://gradio.app/)
- Uses [SmoLAgents](https://github.com/huggingface/smol-ai-agents) framework
- Azure AI for inference
