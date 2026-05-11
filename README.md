# ☁️ Cloud AI Projects
### Two Production-Ready Cloud Applications with AWS & Google Gemini AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20S3-orange?style=for-the-badge&logo=amazon-aws)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-blueviolet?style=for-the-badge&logo=google)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

---

## 📦 Projects Overview

This repository contains **two fully functional, cloud-integrated applications** built as part of a Cloud Computing project. Both are containerized with Docker and designed for deployment on **AWS EC2** with **AWS S3** cloud storage integration.

| # | Project | Description | Port |
|---|---------|-------------|------|
| 1 | 🏥 **MedGuard** | Hospital Patient Registration with AI Duplicate Detection | `5001` |
| 2 | 🤖 **SmartBot** | Generative AI Chatbot powered by Google Gemini 2.5 Flash | `5002` |

---

## 🏥 Project 1 — MedGuard Hospital Patient Registration System

### Overview
A real-world hospital patient management system that solves the critical problem of **duplicate patient records** — which costs the healthcare industry billions annually in misdiagnoses, duplicate billing, and wasted resources.

### ✨ Features
- 🔍 **Fuzzy-Logic Duplicate Detection** — Uses MD5 hashing + SequenceMatcher algorithm to catch exact and near-duplicate patient records (e.g., "Rahul Sharma" vs "Rahul Sharmu")
- 📊 **Confidence Scoring** — Shows exactly which fields matched (Name, Email, Phone) and a similarity percentage
- ✏️ **Full CRUD Operations** — Register, Edit (modal with pre-filled data), and Delete patients with confirmation dialogs
- ☁️ **AWS S3 Integration** — Backs up patient records to S3 cloud storage
- 🔔 **Local Mode Warning** — Prominent banner warns admin when cloud sync is disabled
- 📱 **Responsive Design** — Works on mobile and desktop
- 🔎 **Live Search** — Real-time patient search across name, email, phone, and blood group

### 🛠️ Tech Stack
- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript
- **Cloud:** AWS S3 (boto3), AWS EC2
- **Algorithm:** MD5 Hashing, Difflib SequenceMatcher (Fuzzy Logic)

### 📸 Key Screens
- Dashboard with patient stats, live table, and activity log
- Smart duplicate warning with confidence bar and matched fields breakdown
- Edit patient modal with pre-filled form data

---

## 🤖 Project 2 — SmartBot AI Chatbot

### Overview
A **ChatGPT-like AI assistant** powered by Google's latest **Gemini 2.5 Flash** model. Features real-time streaming responses, voice input, multi-turn conversation memory, and cloud chat log storage on AWS S3.

### ✨ Features
- ⚡ **Streaming Responses** — Text appears word-by-word via Server-Sent Events (SSE), just like ChatGPT
- 🎙️ **Voice Input** — Click the mic button and speak your question using the Web Speech API
- 🧠 **Multi-turn Memory** — Full conversation history maintained server-side per session
- 📝 **Markdown Rendering** — Responses render bold, code blocks, bullet points (via marked.js)
- 📋 **Copy Button** — One-click copy on every bot response
- 🌐 **Real-time Web Search** — Uses Gemini's built-in Google Search tool for current information (e.g., live weather)
- ☁️ **AWS S3 Chat Logs** — Save entire conversation sessions to cloud storage
- 💡 **Suggested Questions** — Quick-start prompts for new users

### 🛠️ Tech Stack
- **Backend:** Python, Flask, Google GenAI SDK (`google-genai`)
- **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript, marked.js
- **AI Model:** Google Gemini 2.5 Flash (with Google Search tool)
- **Cloud:** AWS S3, AWS EC2
- **Streaming:** Server-Sent Events (SSE)

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- A Google Gemini API key ([Get one free](https://aistudio.google.com/))
- (Optional) AWS credentials for S3 sync

### 1. Clone the repository
```bash
git clone https://github.com/shayu07/cloud-projects.git
cd cloud-projects
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create `.env` files in each project folder:

**`project1_redundancy/.env`**
```env
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your_bucket_name
```

**`project2_chatbot/.env`**
```env
GEMINI_API_KEY=your_gemini_api_key_here
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your_bucket_name
```

### 4. Run the applications

**Option A — Run separately:**
```bash
# Terminal 1 — Hospital System
python project1_redundancy/app.py

# Terminal 2 — AI Chatbot
python project2_chatbot/app.py
```

**Option B — Run both with Docker:**
```bash
docker-compose up -d
```

### 5. Open in browser
- 🏥 Hospital System: [http://localhost:5001](http://localhost:5001)
- 🤖 AI Chatbot: [http://localhost:5002](http://localhost:5002)

---

## ☁️ AWS Deployment

Both apps run on a **single AWS EC2 t2.micro instance** (Free Tier eligible).

```
EC2 Server (Ubuntu 22.04)
├── Port 5001 → MedGuard Hospital System
└── Port 5002 → SmartBot AI Chatbot
```

**EC2 Security Group Rules required:**

| Type | Port | Purpose |
|---|---|---|
| SSH | 22 | Server access |
| Custom TCP | 5001 | Hospital app |
| Custom TCP | 5002 | Chatbot app |

---

## 📁 Project Structure

```
cloud-projects/
│
├── project1_redundancy/          # 🏥 MedGuard
│   ├── app.py                    # Flask routes
│   ├── db_utils.py               # SQLite + duplicate detection logic
│   ├── cloud_storage.py          # AWS S3 integration
│   ├── static/
│   │   ├── app.js                # Frontend logic
│   │   └── styles.css            # Dark medical theme
│   └── templates/
│       └── index.html            # Dashboard UI
│
├── project2_chatbot/             # 🤖 SmartBot
│   ├── app.py                    # Flask routes + SSE streaming
│   ├── chatbot_engine.py         # Gemini API + chat sessions
│   ├── cloud_config.py           # AWS S3 chat log storage
│   ├── static/
│   │   ├── app.js                # Streaming + voice input logic
│   │   └── styles.css            # Dark messenger theme
│   └── templates/
│       └── index.html            # Chat UI
│
├── docker-compose.yml            # 🐳 Launch both apps together
├── requirements.txt              # Python dependencies
├── .gitignore                    # Excludes .env, .db, __pycache__
└── README.md                     # This file
```

---

## 🔐 Security

- All API keys are stored in `.env` files which are **excluded from Git** via `.gitignore`
- No secrets are ever exposed to the client browser
- All Gemini API calls happen **server-side** on EC2
- AWS credentials use IAM best practices

---

## 👨‍💻 Author

**Shayu** — [@shayu07](https://github.com/shayu07)

Built with ❤️ as part of a Cloud Computing project demonstrating real-world AWS EC2, S3, and Generative AI integration.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
