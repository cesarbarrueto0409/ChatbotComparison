# ChatBot Comparative

**Simple comparative chat UI and API that queries Azure OpenAI and AWS Bedrock and stores conversations in Redis/MongoDB.** ✅

---

## 📌 Project overview

- **Backend**: FastAPI app (`app/`) exposing POST `/chatbot` which returns responses from two agents: Azure and AWS.
- **Agents**:
  - `AzureAgent` uses Azure OpenAI (configured via `AZURE_OPENAI_*` env vars).
  - `AwsAgent` uses AWS Bedrock (configured via `AWS_*` env vars).
- **Memory**:
  - `RedisMemory` keeps short-term conversation history (TTL)
  - `MongoMemory` persists messages for auditing and analysis
- **Frontend**: static files in `frontend/` (`index.html`, `script.js`, `styles.css`) showing two side-by-side chat boxes.
- **Deployment**: `Dockerfile` and `docker-compose.yml` provide an easy local setup (API + Redis).

---

## ⚙️ How it works (quick flow)

1. User types a message in the frontend; a `session_id` is stored in `localStorage`.
2. Frontend POSTs `{ session_id, message }` to `http://localhost:3000/chatbot`.
3. Backend loads session history from Redis, appends the user message, saves to Redis and MongoDB, calls each agent, saves responses to MongoDB, and returns `{ azure, aws }`.
4. Frontend displays each agent's answer in its column.

---

## ▶️ Run locally (recommended: Docker)

### A) Docker Compose (recommended)

1. Create a `.env` file (see list below).
2. Build & start services:

```bash
docker compose up --build
```

3. Backend will be available at `http://localhost:3000` and Redis at `6379`.
4. Open `frontend/index.html` in a browser (or serve with `python -m http.server` inside `frontend/`).

### B) Local Python (no Docker)

1. Create a venv and activate it:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (see variables below) and start uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

4. Open `frontend/index.html` or serve with a static server.

---

## 🔐 Environment variables (put these in `.env`) 

- `AZURE_OPENAI_KEY` (SECRET)
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_VERSION`
- `AWS_BEARER_TOKEN_BEDROCK` (SECRET)
- `AWS_REGION`
- `AWS_BEDROCK_MODEL_ID`
- `URI_MONGODB` (SECRET — contains credentials)
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_TTL`

> Add a `.env.example` with empty placeholder values and commit that instead of a real `.env` file.

---

## ⚠️ Security notes

- **Do not commit** your real `.env` file. If secrets were committed, rotate them immediately and remove them from Git history (use BFG or `git filter-repo`).
- Add `.env` to `.gitignore` (see `.env.example` for placeholders).
- For production, use a secrets manager (AWS Secrets Manager, Azure Key Vault) and tighten CORS and network rules.

---

## 🛠️ Files of interest

- `app/main.py` — app entry (loads `.env` and configures CORS)
- `app/router.py` — chat endpoint and agent orchestration
- `app/chatbot/ChatController.py` — conversation flow & memory interaction
- `app/chatbot/aiAgent/` — `AzureAgent.py`, `AwsAgent.py`
- `app/chatbot/memory/` — `RedisMemory.py`, `MongoMemory.py`
- `frontend/` — UI files (`index.html`, `script.js`, `styles.css`)

---

## ✅ Next steps I recommend

- Add `.env` to `.gitignore` and commit a `.env.example` with placeholders.
- Rotate any exposed keys found in the repo.
- Consider enabling authentication for Redis and protecting MongoDB access.

---

If you want, I can add `.gitignore` and `.env.example`, and help remove any committed `.env` from git history.
