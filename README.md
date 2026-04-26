# ⚡ PromptForge — AI Prompt Optimizer

Ek Django-based web application jo aapke simple, vague prompts ko automatically structured, detailed aur powerful prompts me convert karta hai — taaki AI tools se behtar results milein.

## 🚀 Features

- **Automatic Prompt Optimization** — Raw question → Structured prompt with role, context, format
- **OpenAI API Integration** — Optimized prompt ko directly AI ko bhejne ki suvidha
- **Local Fallback** — API key ke bina bhi rule-based optimization kaam karta hai
- **Prompt History** — Saare past prompts SQLite me store hote hain
- **Category Detection** — Coding, Education, Business, Creative writing etc.
- **Copy to Clipboard** — One-click copy optimized prompt
- **Dark Cyberpunk UI** — Beautiful, modern interface

## 📦 Installation

### Step 1: Python aur pip install karein (agar nahi hai)
```bash
python --version  # Python 3.8+ chahiye
```

### Step 2: Virtual environment banayein
```bash
cd prompt_optimizer
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Dependencies install karein
```bash
pip install -r requirements.txt
```

### Step 4: Database setup
```bash
python manage.py migrate
```

### Step 5: Server chalayein
```bash
python manage.py runserver
```

### Step 6: Browser mein kholein
```
http://127.0.0.1:8000
```

---

## 🔑 OpenAI API Key (Optional)

Live AI responses ke liye:
1. [OpenAI Platform](https://platform.openai.com) pe jaayein
2. API key banaayein
3. App mein "API Configuration" expand karein
4. Key enter karein (sirf memory mein store hoti hai, save nahi hoti)

**Bina API key ke bhi app kaam karta hai** — rule-based local optimization use hoti hai.

---

## 📁 Project Structure

```
prompt_optimizer/
├── manage.py
├── requirements.txt
├── db.sqlite3          (auto-created after migrate)
├── prompt_optimizer/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── optimizer/
│   ├── models.py       (PromptHistory model)
│   ├── views.py        (All logic + API calls)
│   └── urls.py
└── templates/
    └── optimizer/
        ├── base.html
        ├── index.html
        ├── history.html
        └── history_detail.html
```

## 🧠 How It Works

1. **User** simple question type karta hai (e.g., "tell me about python")
2. **System** us prompt ko analyze karta hai
3. **Optimization** — Role + Context + Format + Constraints add hota hai
4. **Output** — Structured, detailed prompt jo AI se 10x better answer dilata hai
5. **Optional** — Optimized prompt OpenAI API ko bheja ja sakta hai

## ⚙️ Environment Variables

```bash
# Optional: settings.py me hardcode karne ki jagah
export OPENAI_API_KEY=sk-your-key-here
python manage.py runserver
```

---

Made with ❤️ using Django
