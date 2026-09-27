from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import engine

configure_logging()
settings = get_settings()

# Mensagens de erro em português, para que a interface mostre algo que o
# usuário entenda em vez do texto técnico do Pydantic.
FIELD_LABELS: dict[str, str] = {
    "ano": "Ano",
    "page": "Página",
    "size": "Quantidade por página",
    "titulo": "Título",
    "genero": "Gênero",
    "status_filme": "Status do filme",
    "nome": "Nome",
    "nota": "Nota",
    "comentario": "Comentário",
    "nome_pessoa": "Nome da pessoa",
    "tipo_pessoa": "Tipo de pessoa",
    "url_poster": "URL do pôster",
    "url_backdrop": "URL da imagem de fundo",
    "id_filme": "Identificador do filme",
    "sk_movie_id": "Filme",
    "sk_movie_review_id": "Avaliação",
    "sk_person_id": "Pessoa",
}

GENERIC_MESSAGES: dict[str, str] = {
    "Field required": "campo obrigatório",
    "Input should be a valid integer": "informe um número inteiro",
    "Input should be a valid number": "informe um número válido",
    "Input should be a valid string": "informe um texto",
    "Input should be a valid list": "informe uma lista",
    "Value error": "valor inválido",
    "Input should be 'Ator', 'Diretor' or 'Roteirista'": "escolha Ator, Diretor ou Roteirista",
}

UNKNOWN_ERROR = "Confira os dados informados e tente novamente."

MIN_PATTERN = "greater than or equal to"
MAX_PATTERN = "less than or equal to"


def _extract_bound(raw: str) -> str | None:
    """Pega o número citado na mensagem do Pydantic (ex.: "... or equal to 1800")."""
    return next((part for part in raw.split() if part.replace(".", "", 1).isdigit()), None)


def _friendly_validation_message(error: dict) -> str:
    """Traduz um erro de validação do Pydantic para uma mensagem legível."""
    location = error.get("loc") or []
    field = location[-1] if location and isinstance(location[-1], str) else None
    label = FIELD_LABELS.get(field or "", field or "")
    raw = str(error.get("msg") or "").strip()

    if not raw or raw.startswith("Assertion failed"):
        return UNKNOWN_ERROR

    # "Input should be greater than or equal to 1800" -> "Ano deve ser no mínimo 1800."
    if (MIN_PATTERN in raw or MAX_PATTERN in raw) and (bound := _extract_bound(raw)):
        verbo = "no mínimo" if MIN_PATTERN in raw else "no máximo"
        alvo = f"{label} deve ser {verbo} {bound}." if label else None
        return alvo or f"O valor deve ser {verbo} {bound}."

    if not label:
        return f"{raw}."

    # O Pydantic às vezes alonga a mensagem com o motivo do erro
    # (ex.: "Input should be a valid integer, unable to parse string as an
    # integer"), então o texto genérico é procurado por prefixo.
    for generic, traduzido in GENERIC_MESSAGES.items():
        if raw.startswith(generic):
            return f"{label}: {traduzido}."

    # "String should have at least 1 character" / "Input should be at least 1"
    if ("at least" in raw or "at most" in raw) and (bound := _extract_bound(raw)):
        unidade = " caracteres" if "characters" in raw else ""
        verbo = "no mínimo" if "at least" in raw else "no máximo"
        return f"{label} deve ser {verbo} {bound}{unidade}."

    return f"{label}: {raw}."



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Libera recursos de infraestrutura quando a aplicação é encerrada."""

    del app
    # A criação/evolução do schema é responsabilidade exclusiva do Alembic.
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Devolve 422 com mensagens em português, sem o texto cru do Pydantic."""
        del request
        messages = [_friendly_validation_message(error) for error in exc.errors()]

        return JSONResponse(
            status_code=422,
            content={"detail": " ".join(dict.fromkeys(messages)) or UNKNOWN_ERROR},
        )

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
