# 🎬 CineDex

O **CineDex** é um sistema de catálogo e avaliação de filmes inspirado em plataformas como o Letterboxd.

O CineDex é uma aplicação web de catálogo e avaliação de filmes, criada para explorar o universo cinematográfico de forma completa. Os usuários podem pesquisar e filtrar filmes, consultar detalhes como sinopse, elenco, direção, roteiro e avaliações, além de registrar suas próprias notas e comentários. A plataforma também permite pesquisar atores, diretores e roteiristas e descobrir os filmes dos quais cada profissional participou. Para o gerenciamento do catálogo, o sistema possibilita cadastrar, editar e excluir filmes.

---

## 🛠️ Tecnologias Utilizadas

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-4B5563?style=for-the-badge&logoColor=white)

### Frontend

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

### Banco de Dados

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## ✨ Funcionalidades

### 🎬 Catálogo de filmes

- Visualização do catálogo de filmes.
- Paginação dos resultados.
- Busca por título.
- Filtros por ano, gênero e status.
- Visualização das informações do filme.

### ⭐ Avaliações

- Cadastro de avaliações.
- Notas de 1 a 5.
- Comentários dos usuários.
- Visualização das avaliações de um filme.
- Cálculo da média das avaliações.
- Quantidade de avaliações por filme.

### ⚙️ Gerenciamento de filmes

- Cadastro de novos filmes.
- Edição de filmes.
- Exclusão de filmes.
- Consulta individual de filmes.

### 👥 Pessoas

- Informações sobre atores, diretores e roteiristas.
- Associação entre pessoas e filmes.

---

# 📁 Estrutura do Projeto

```text
CineDex/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   │
│   │   ├── movies/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   │
│   │   ├── reviews/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── services.py
│   │   │   └── router.py
│   │   │
│   │   ├── people/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   │
│   │   └── main.py
│   │
│   ├── migrations/
│   │   └── versions/
│   │
│   ├── requirements.txt
│   └── rocketlab.db
│
├── frontend/
│   ├── public/
│   │
│   ├── src/
│   │   ├── assets/
│   │   │
│   │   ├── components/
│   │   │   ├── Header/
│   │   │   ├── MovieCard/
│   │   │   ├── MovieGrid/
│   │   │   ├── SearchBar/
│   │   │   ├── Pagination/
│   │   │   ├── Rating/
│   │   │   └── ReviewCard/
│   │   │
│   │   ├── pages/
│   │   │   ├── Home/
│   │   │   ├── Movies/
│   │   │   ├── MovieDetails/
│   │   │   ├── AddMovie/
│   │   │   ├── EditMovie/
│   │   │   └── Person/
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── movieService.ts
│   │   │   ├── reviewService.ts
│   │   │   └── peopleService.ts
│   │   │
│   │   ├── types/
│   │   │   ├── movie.ts
│   │   │   ├── review.ts
│   │   │   └── person.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── .gitignore
└── README.md
```

---

# 📋 Requisitos Prévios

Para executar o projeto, é necessário ter instalado:

- **Git**
- **Python 3**
- **Node.js**
- **npm**

---

# 🚀 Como Iniciar a Aplicação

## 1. Clonar o repositório

```bash
git clone https://github.com/Sofia1653/CineDex.git
```

Acesse a pasta do projeto:

```bash
cd CineDex
```

---

## 2. Configuração do Backend

### Criar a virtual environment

Na raiz do projeto:

```powershell
python -m venv .venv
```

### Ativar a virtual environment

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar as dependências

```powershell
cd backend
pip install -r requirements.txt
```

### Executar as migrations

```powershell
alembic upgrade head
```

### Iniciar o servidor

```powershell
fastapi dev app/main.py
```

O backend estará disponível em:

```text
http://127.0.0.1:8000
```

### Documentação da API

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 🎨 3. Configuração do Frontend

Abra **outro terminal** na raiz do projeto.

Acesse a pasta:

```powershell
cd frontend
```

Instale as dependências:

```powershell
npm install
```

Execute o projeto:

```powershell
npm run dev
```

O frontend estará disponível em:

```text
http://localhost:5173
```

---

# 🔄 Executando Backend e Frontend

É necessário manter **dois terminais abertos**.

### Terminal 1 — Backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
alembic upgrade head
fastapi dev app/main.py
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

---

# 🌐 Acessos da Aplicação

| Serviço | Porta | URL |
|---|---:|---|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 8000 | http://127.0.0.1:8000 |
| Swagger | 8000 | http://127.0.0.1:8000/docs |
| ReDoc | 8000 | http://127.0.0.1:8000/redoc |

