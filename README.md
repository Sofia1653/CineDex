# CineDex

## ▶️ Como executar o projeto

### 🔙 Backend

Abra um terminal na raiz do projeto e execute:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
alembic upgrade head
fastapi dev app/main.py
```

O backend estará disponível em:

```text
http://127.0.0.1:8000
```

Documentação da API:

```text
http://127.0.0.1:8000/docs
```

---

### 🎨 Frontend

Abra **outro terminal** na raiz do projeto e execute:

```powershell
cd frontend
npm install
npm run dev
```

O frontend estará disponível em:

```text
http://localhost:5173
```

---

### 🚀 Executando os dois

Você precisa manter **dois terminais abertos**:

**Terminal 1 — Backend**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
alembic upgrade head
fastapi dev app/main.py
```

**Terminal 2 — Frontend**

```powershell
cd frontend
npm run dev
```