"""Repara o banco já populado com os ajustes de qualidade de dados.

Executa duas correções idempotentes, sem recarregar os CSVs:

1. `dim_people` normaliza os nomes corrompidos pelo dataset de origem (aspas
   orfas no início/fim, inicial minúscula, espaços duplicados) e remove os
   registros que não são pessoas (caminhos de imagem e códigos numéricos),
   junto com as linhas órfãs de `bridge_movie_person`.
2. `dim_reviews` é recalculado a partir das avaliações reais em `movie_reviews`,
   para que a nota e a quantidade exibidas no catálogo batam com as resenhas.

Uso (a partir de `backend/`):
    python -m scripts.fix_data
    python -m scripts.fix_data --db-path caminho/para/rocketlab.db
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from scripts.data_cleaning import normalize_person_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fix_data")

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "rocketlab.db"


def fix_person_names(con: sqlite3.Connection) -> None:
    """Normaliza `dim_people.nome_pessoa` e descarta os registros inválidos.

    Ao normalizar, dois registros diferentes podem virar o mesmo nome (por exemplo
    `"michelle Deguara` e `Michelle Deguara`). Nesse caso um dos dois é removido e
    os filmes em que ele aparecia são vinculados ao sobrevivente, para que a
    filmografia não perca ninguém.
    """
    rows = con.execute("SELECT sk_person_id, nome_pessoa, tipo_pessoa FROM dim_people;").fetchall()

    # (nome, tipo) -> sk do registro que sobrevive (o primeiro encontrado).
    sobrevivo: dict[tuple[str, str], str] = {}
    atualizacoes: list[tuple[str, str, str]] = []
    duplicados: dict[str, str] = {}
    invalidos: list[str] = []

    for sk_person_id, nome_bruto, tipo in rows:
        nome = normalize_person_name(nome_bruto)

        if not nome:
            invalidos.append(sk_person_id)
            continue

        anterior = sobrevivo.get((nome, tipo))
        if anterior is not None:
            duplicados[sk_person_id] = anterior
            continue

        sobrevivo[(nome, tipo)] = sk_person_id
        if nome != nome_bruto:
            atualizacoes.append((nome, sk_person_id, tipo))

    # Os duplicados saem antes de qualquer renomeação, com os filmes deles
    # repassados para o sobrevivente.
    for sk_duplicado, sk_sobrevivo in duplicados.items():
        # `INSERT OR IGNORE` mantém a primeira ocorrência quando o filme já está
        # ligado ao sobrevivente, respeitando a chave primária composta.
        con.execute(
            "INSERT OR IGNORE INTO bridge_movie_person (sk_movie_id, sk_person_id) "
            "SELECT sk_movie_id, ? FROM bridge_movie_person WHERE sk_person_id = ?;",
            (sk_sobrevivo, sk_duplicado),
        )
        con.execute("DELETE FROM bridge_movie_person WHERE sk_person_id = ?;", (sk_duplicado,))
        con.execute("DELETE FROM dim_people WHERE sk_person_id = ?;", (sk_duplicado,))

    for sk_invalido in invalidos:
        con.execute("DELETE FROM bridge_movie_person WHERE sk_person_id = ?;", (sk_invalido,))
        con.execute("DELETE FROM dim_people WHERE sk_person_id = ?;", (sk_invalido,))

    # A renomeação acontece em duas fases porque `dim_people` tem índice único em
    # (nome_pessoa, tipo_pessoa): o novo nome de uma linha pode ser o nome atual de
    # outra. Primeiro cada linha vai para um nome temporário único, liberando todos
    # os nomes originais, e só depois recebe o nome definitivo.
    temporarios = [(f"~tmp{sk_person_id}", sk_person_id) for _, sk_person_id, _ in atualizacoes]
    con.executemany("UPDATE dim_people SET nome_pessoa = ? WHERE sk_person_id = ?;", temporarios)
    con.executemany(
        "UPDATE dim_people SET nome_pessoa = ? WHERE sk_person_id = ?;",
        [(nome, sk_person_id) for nome, sk_person_id, _ in atualizacoes],
    )

    con.commit()
    logger.info("dim_people: %d nomes normalizados", len(atualizacoes))
    logger.info("dim_people: %d duplicados unificados no nome corrigido", len(duplicados))
    logger.info("dim_people: %d registros removidos por não serem pessoas", len(invalidos))


def rebuild_dim_reviews(con: sqlite3.Connection) -> None:
    """Recalcula `dim_reviews` para bater com as avaliações reais."""
    agregados = con.execute(
        """
        SELECT sk_movie_id, count(*), round(avg(nota), 2)
        FROM movie_reviews
        GROUP BY sk_movie_id
        """
    ).fetchall()

    con.execute("DELETE FROM dim_reviews;")
    con.executemany(
        """
        INSERT INTO dim_reviews (
            sk_review_id, sk_movie_id, qtd_avaliacoes_usuarios, nota_media_usuarios
        ) VALUES (?, ?, ?, ?);
        """,
        [
            (sha256(uuid4().bytes).hexdigest(), sk_movie_id, total, media)
            for sk_movie_id, total, media in agregados
        ],
    )
    con.commit()
    logger.info("dim_reviews: %d resumos recalculados", len(agregados))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Corrige nomes de pessoas e resumos de avaliações no rocketlab.db"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Caminho para o banco de dados SQLite (padrão: backend/rocketlab.db)",
    )
    args = parser.parse_args()

    if not args.db_path.exists():
        logger.error("Banco de dados não encontrado: %s", args.db_path)
        sys.exit(1)

    con = sqlite3.connect(str(args.db_path))
    try:
        con.execute("PRAGMA synchronous = OFF;")
        con.execute("PRAGMA journal_mode = MEMORY;")

        logger.info("Corrigindo dim_people...")
        fix_person_names(con)

        logger.info("Recalculando dim_reviews...")
        rebuild_dim_reviews(con)

        violacoes = con.execute("PRAGMA foreign_key_check;").fetchall()
        if violacoes:
            logger.error("Violações de integridade referencial: %s", violacoes)
            sys.exit(1)

        logger.info("Correções aplicadas com sucesso em %s", args.db_path.name)
    finally:
        con.close()


if __name__ == "__main__":
    main()
