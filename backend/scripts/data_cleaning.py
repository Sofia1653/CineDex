"""Regras de limpeza aplicadas aos CSVs do CineDex antes de popular o banco.

Fica em um módulo próprio porque tanto o `seed` quanto o script de reparo
(`fix_data`) precisam das mesmas regras, para que um banco recém-criado e um
banco já existente terminem sempre com os mesmos dados.
"""

from __future__ import annotations

import re

# O dataset de origem (TMDB) traz registros quebrados em `dim_people`:
#   - aspas orfas no início/fim, como `"michelle Deguara` ou `'poo' Ram`;
#   - inicial minúscula junto com a aspa, como `"josé A. Marín`;
#   - nomes que na verdade são caminhos de imagem, como `/abc123.jpg`;
#   - nomes puramente numéricos, como `3176` ou `0.876`.
# Os três últimos tipos não são pessoas e poluem a listagem, então são descartados.
ASPAS = "\"'“”‘’`´"
_SLUG_ARQUIVO = re.compile(r"^/?[\w.\-]+\.(?:jpg|jpeg|png|gif|webp)$", re.IGNORECASE)
_TEM_LETRA = re.compile(r"[^\W\d_]", re.UNICODE)


def clean_person_name(val: str | None) -> str | None:
    """Normaliza o nome de uma pessoa, devolvendo None quando não é um nome válido.

    Remove as aspas orfas do dataset de origem, resolve aspas duplas usadas para
    escapar apelidos (`""kia B""` vira `"kia B"`), colapsa espaços repetidos e
    devolve None para entradas que não são nomes (slug de imagem ou só dígitos).
    """
    if val is None:
        return None

    nome = val.strip()
    if not nome:
        return None

    # Abreviações e apelidos entre aspas duplas viram aspas simples.
    nome = re.sub(r'""+', '"', nome)

    # Aspas de fechamento que sobraram de um CSV com escape inconsistente.
    while nome and nome[-1] in ASPAS:
        nome = nome[:-1].rstrip()

    # Remove as aspas que sobraram no início e normaliza espaços.
    nome = re.sub(rf"^[{re.escape(ASPAS)}]+", "", nome)
    nome = re.sub(r"\s+", " ", nome).strip()

    if not nome:
        return None

    # Não é um nome: é o caminho de uma imagem quebrada ou um código numérico.
    if _SLUG_ARQUIVO.match(nome) or "/" in nome:
        return None
    if not _TEM_LETRA.search(nome):
        return None

    return nome


def fix_person_name_case(nome: str) -> str:
    """Restaura a inicial maiúscula de nomes que vieram minúsculos do dataset."""
    for i, char in enumerate(nome):
        if char.isalpha():
            if char.islower():
                return nome[:i] + char.upper() + nome[i + 1 :]
            return nome
    return nome


def normalize_person_name(val: str | None) -> str | None:
    """Atalho para `clean_person_name` seguido de `fix_person_name_case`."""
    nome = clean_person_name(val)

    if not nome or not val:
        return nome

    # A inicial minúscula do dataset sempre vem acompanhada da aspa de abertura,
    # então a caixa só é restaurada nos nomes que tinham esse defeito.
    if val.strip()[:1] in ASPAS:
        return fix_person_name_case(nome)

    return nome
