"""Script de carga inicial (seed) do banco de dados do CineDex / RocketLab.

Executa a leitura dos arquivos CSV do diretório de dados, realiza limpeza,
tratamento de nulos/duplicados e povoa o banco SQLite seguindo a ordem de
integridade referencial:
  1. dim_genres
  2. dim_companies
  3. dim_people
  4. dim_movies
  5. bridge_movie_genre
  6. bridge_movie_company
  7. bridge_movie_person
  8. fact_movies_performance
  9. dim_reviews
  10. movie_reviews
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Configuração de logging informativo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed")

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = BASE_DIR / "rocketlab.db"

VALID_PERSON_TYPES = frozenset({"Ator", "Diretor", "Roteirista"})


def clean_str(val: str | None) -> str | None:
    """Remove espaços extras e converte strings vazias em None."""
    if val is None:
        return None
    cleaned = val.strip()
    return cleaned if cleaned else None


def clean_int(val: str | None, default: int | None = None) -> int | None:
    """Converte com segurança valores textuais para int, suportando representações em float."""
    if val is None:
        return default
    cleaned = val.strip()
    if not cleaned:
        return default
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return default


def clean_float(val: str | None, default: float | None = None) -> float | None:
    """Converte valores textuais para float, tratando nulos e formatação incorreta."""
    if val is None:
        return default
    cleaned = val.strip()
    if not cleaned:
        return default
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def clean_date(val: str | None) -> str | None:
    """Valida e limpa datas no formato YYYY-MM-DD."""
    cleaned = clean_str(val)
    if not cleaned:
        return None
    # Verifica formato básico YYYY-MM-DD
    if len(cleaned) == 10 and cleaned[4] == "-" and cleaned[7] == "-":
        return cleaned
    return None


def clear_database_tables(con: sqlite3.Connection) -> None:
    """Remove dados existentes das tabelas na ordem inversa de dependências."""
    tables = [
        "movie_reviews",
        "dim_reviews",
        "fact_movies_performance",
        "bridge_movie_person",
        "bridge_movie_company",
        "bridge_movie_genre",
        "dim_people",
        "dim_companies",
        "dim_genres",
        "dim_movies",
    ]
    logger.info("Limpando tabelas existentes para garantir idempotência...")
    cursor = con.cursor()
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
    con.commit()
    logger.info("Tabelas limpas com sucesso.")


def seed_genres(con: sqlite3.Connection, data_dir: Path) -> set[str]:
    """Lê e insere gêneros em dim_genres."""
    csv_file = data_dir / "dim_genres.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando dim_genres.", csv_file.name)
        return set()

    t0 = time.time()
    valid_ids: set[str] = set()
    seen_names: set[str] = set()
    records: list[tuple[str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_genre_id"))
            nome = clean_str(row.get("nome_genero"))
            if not sk or not nome:
                continue
            if sk in valid_ids or nome in seen_names:
                continue
            valid_ids.add(sk)
            seen_names.add(nome)
            records.append((sk, nome))

    con.executemany(
        "INSERT INTO dim_genres (sk_genre_id, nome_genero) VALUES (?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "dim_genres: %d registros inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )
    return valid_ids


def seed_companies(con: sqlite3.Connection, data_dir: Path) -> set[str]:
    """Lê e insere produtoras em dim_companies."""
    csv_file = data_dir / "dim_companies.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando dim_companies.", csv_file.name)
        return set()

    t0 = time.time()
    valid_ids: set[str] = set()
    seen_names: set[str] = set()
    records: list[tuple[str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_company_id"))
            nome = clean_str(row.get("nome_produtora"))
            if not sk or not nome:
                continue
            if sk in valid_ids or nome in seen_names:
                continue
            valid_ids.add(sk)
            seen_names.add(nome)
            records.append((sk, nome))

    con.executemany(
        "INSERT INTO dim_companies (sk_company_id, nome_produtora) VALUES (?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "dim_companies: %d registros inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )
    return valid_ids


def seed_people(con: sqlite3.Connection, data_dir: Path) -> set[str]:
    """Lê e insere pessoas em dim_people com validação de tipo."""
    csv_file = data_dir / "dim_people.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando dim_people.", csv_file.name)
        return set()

    t0 = time.time()
    valid_ids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    records: list[tuple[str, str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_person_id"))
            nome = clean_str(row.get("nome_pessoa"))
            tipo = clean_str(row.get("tipo_pessoa"))
            if not sk or not nome or not tipo:
                continue
            if tipo not in VALID_PERSON_TYPES:
                continue
            pair = (nome, tipo)
            if sk in valid_ids or pair in seen_pairs:
                continue
            valid_ids.add(sk)
            seen_pairs.add(pair)
            records.append((sk, nome, tipo))

    con.executemany(
        "INSERT INTO dim_people (sk_person_id, nome_pessoa, tipo_pessoa) VALUES (?, ?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "dim_people: %d registros inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )
    return valid_ids


def seed_movies(con: sqlite3.Connection, data_dir: Path) -> set[str]:
    """Lê e insere filmes em dim_movies com limpeza de datas e metadados."""
    csv_file = data_dir / "dim_movies.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando dim_movies.", csv_file.name)
        return set()

    t0 = time.time()
    valid_ids: set[str] = set()
    seen_id_filme: set[str] = set()
    records: list[
        tuple[
            str,
            str,
            str,
            str | None,
            int | None,
            int | None,
            str | None,
            str | None,
            str | None,
            str | None,
        ]
    ] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_movie_id"))
            id_filme = clean_str(row.get("id_filme"))
            titulo = clean_str(row.get("titulo"))
            if not sk or not id_filme or not titulo:
                continue
            if sk in valid_ids or id_filme in seen_id_filme:
                continue
            valid_ids.add(sk)
            seen_id_filme.add(id_filme)

            data_lanc = clean_date(row.get("data_lancamento"))
            ano = clean_int(row.get("ano_lancamento"))
            if ano is None and data_lanc:
                try:
                    ano = int(data_lanc[:4])
                except (ValueError, TypeError):
                    ano = None

            duracao = clean_int(row.get("duracao_minutos"))
            status = clean_str(row.get("status_filme"))
            sinopse = clean_str(row.get("sinopse"))
            url_poster = clean_str(row.get("url_poster"))
            url_backdrop = clean_str(row.get("url_backdrop"))

            records.append(
                (
                    sk,
                    id_filme,
                    titulo,
                    data_lanc,
                    ano,
                    duracao,
                    status,
                    sinopse,
                    url_poster,
                    url_backdrop,
                )
            )

    con.executemany(
        """
        INSERT INTO dim_movies (
            sk_movie_id, id_filme, titulo, data_lancamento, ano_lancamento,
            duracao_minutos, status_filme, sinopse, url_poster, url_backdrop
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    con.commit()
    logger.info(
        "dim_movies: %d registros inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )
    return valid_ids


def seed_bridge_movie_genre(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
    valid_genre_ids: set[str],
) -> None:
    """Insere relacionamentos entre filmes e gêneros em bridge_movie_genre."""
    csv_file = data_dir / "bridge_movie_genre.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando bridge_movie_genre.", csv_file.name)
        return

    t0 = time.time()
    seen_pairs: set[tuple[str, str]] = set()
    records: list[tuple[str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = clean_str(row.get("sk_movie_id"))
            g = clean_str(row.get("sk_genre_id"))
            if not m or not g:
                continue
            if m in valid_movie_ids and g in valid_genre_ids:
                pair = (m, g)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    records.append(pair)

    con.executemany(
        "INSERT INTO bridge_movie_genre (sk_movie_id, sk_genre_id) VALUES (?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "bridge_movie_genre: %d relacionamentos inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )


def seed_bridge_movie_company(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
    valid_company_ids: set[str],
) -> None:
    """Insere relacionamentos entre filmes e produtoras em bridge_movie_company."""
    csv_file = data_dir / "bridge_movie_company.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando bridge_movie_company.", csv_file.name)
        return

    t0 = time.time()
    seen_pairs: set[tuple[str, str]] = set()
    records: list[tuple[str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = clean_str(row.get("sk_movie_id"))
            c = clean_str(row.get("sk_company_id"))
            if not m or not c:
                continue
            if m in valid_movie_ids and c in valid_company_ids:
                pair = (m, c)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    records.append(pair)

    con.executemany(
        "INSERT INTO bridge_movie_company (sk_movie_id, sk_company_id) VALUES (?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "bridge_movie_company: %d relacionamentos inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )


def seed_bridge_movie_person(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
    valid_person_ids: set[str],
) -> None:
    """Insere relacionamentos entre filmes e pessoas em bridge_movie_person."""
    csv_file = data_dir / "bridge_movie_person.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando bridge_movie_person.", csv_file.name)
        return

    t0 = time.time()
    seen_pairs: set[tuple[str, str]] = set()
    records: list[tuple[str, str]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = clean_str(row.get("sk_movie_id"))
            p = clean_str(row.get("sk_person_id"))
            if not m or not p:
                continue
            if m in valid_movie_ids and p in valid_person_ids:
                pair = (m, p)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    records.append(pair)

    con.executemany(
        "INSERT INTO bridge_movie_person (sk_movie_id, sk_person_id) VALUES (?, ?);",
        records,
    )
    con.commit()
    logger.info(
        "bridge_movie_person: %d relacionamentos inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )


def seed_fact_performance(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
) -> None:
    """Insere métricas financeiras e de engajamento em fact_movies_performance."""
    csv_file = data_dir / "fact_movies_performance.csv"
    if not csv_file.exists():
        logger.warning(
            "Arquivo %s não encontrado. Pulando fact_movies_performance.", csv_file.name
        )
        return

    t0 = time.time()
    seen_ids: set[str] = set()
    records: list[
        tuple[
            str,
            float | None,
            float | None,
            float,
            float | None,
            float | None,
            float,
            float | None,
            float | None,
            int | None,
            float | None,
            int | None,
        ]
    ] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = clean_str(row.get("sk_movie_id"))
            if not m or m not in valid_movie_ids or m in seen_ids:
                continue
            seen_ids.add(m)

            orc_usd = clean_float(row.get("orcamento_usd"))
            rec_usd = clean_float(row.get("receita_usd"))
            luc_usd = clean_float(row.get("lucro_usd"), default=0.0) or 0.0

            orc_brl = clean_float(row.get("orcamento_brl"))
            rec_brl = clean_float(row.get("receita_brl"))
            luc_brl = clean_float(row.get("lucro_brl"), default=0.0) or 0.0

            pop = clean_float(row.get("popularidade"))
            n_tmdb = clean_float(row.get("nota_tmdb"))
            q_tmdb = clean_int(row.get("qtd_tmdb"))
            n_imdb = clean_float(row.get("nota_imdb"))
            q_imdb = clean_int(row.get("qtd_imdb"))

            records.append(
                (
                    m,
                    orc_usd,
                    rec_usd,
                    luc_usd,
                    orc_brl,
                    rec_brl,
                    luc_brl,
                    pop,
                    n_tmdb,
                    q_tmdb,
                    n_imdb,
                    q_imdb,
                )
            )

    con.executemany(
        """
        INSERT INTO fact_movies_performance (
            sk_movie_id, orcamento_usd, receita_usd, lucro_usd,
            orcamento_brl, receita_brl, lucro_brl, popularidade,
            nota_tmdb, qtd_tmdb, nota_imdb, qtd_imdb
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    con.commit()
    logger.info(
        "fact_movies_performance: %d registros inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )


def seed_dim_reviews(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
) -> None:
    """Insere resumo consolidado das avaliações em dim_reviews."""
    csv_file = data_dir / "dim_reviews.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando dim_reviews.", csv_file.name)
        return

    t0 = time.time()
    seen_review_ids: set[str] = set()
    seen_movie_ids: set[str] = set()
    records: list[tuple[str, str, int, float | None]] = []

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_review_id"))
            m = clean_str(row.get("sk_movie_id"))
            if not sk or not m:
                continue
            if m not in valid_movie_ids or sk in seen_review_ids or m in seen_movie_ids:
                continue
            seen_review_ids.add(sk)
            seen_movie_ids.add(m)

            qtd = clean_int(row.get("qtd_avaliacoes_usuarios"), default=0) or 0
            nota = clean_float(row.get("nota_media_usuarios"))
            records.append((sk, m, qtd, nota))

    con.executemany(
        """
        INSERT INTO dim_reviews (
            sk_review_id, sk_movie_id, qtd_avaliacoes_usuarios, nota_media_usuarios
        ) VALUES (?, ?, ?, ?);
        """,
        records,
    )
    con.commit()
    logger.info(
        "dim_reviews: %d resumos inseridos em %.2fs",
        len(records),
        time.time() - t0,
    )


def seed_movie_reviews(
    con: sqlite3.Connection,
    data_dir: Path,
    valid_movie_ids: set[str],
) -> None:
    """Insere avaliações individuais em movie_reviews com validação de escala (0 a 10)."""
    csv_file = data_dir / "movies_reviews.csv"
    if not csv_file.exists():
        logger.warning("Arquivo %s não encontrado. Pulando movie_reviews.", csv_file.name)
        return

    t0 = time.time()
    seen_review_ids: set[str] = set()
    records: list[tuple[str, str, str, float, str, str]] = []
    default_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sk = clean_str(row.get("sk_movie_review_id"))
            m = clean_str(row.get("sk_movie_id"))
            if not sk or not m or m not in valid_movie_ids or sk in seen_review_ids:
                continue

            nota_val = clean_float(row.get("nota"))
            if nota_val is None:
                continue
            # Garante restrição de nota entre 0 e 10
            nota = max(0.0, min(10.0, nota_val))

            nome = clean_str(row.get("nome")) or "Anônimo"
            comentario = clean_str(row.get("comentario")) or ""

            seen_review_ids.add(sk)
            records.append((sk, m, nome, nota, comentario, default_now))

    con.executemany(
        """
        INSERT INTO movie_reviews (
            sk_movie_review_id, sk_movie_id, nome, nota, comentario, created_at
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    con.commit()
    logger.info(
        "movie_reviews: %d avaliações inseridas em %.2fs",
        len(records),
        time.time() - t0,
    )


def run_seed(data_dir: Path, db_path: Path, clear_existing: bool = True) -> None:
    """Orquestra todo o processo de carga de dados e validação no banco SQLite."""
    start_time = time.time()
    logger.info("Iniciando processo de seed...")
    logger.info("Diretório de dados: %s", data_dir)
    logger.info("Banco de dados SQLite: %s", db_path)

    if not data_dir.is_dir():
        logger.error("Diretório de dados não encontrado: %s", data_dir)
        sys.exit(1)

    if not db_path.exists():
        logger.error(
            "Arquivo de banco de dados não encontrado em %s. Execute as migrações primeiro.",
            db_path,
        )
        sys.exit(1)

    con = sqlite3.connect(str(db_path))

    try:
        # Otimizações de I/O e cache para carga em lote massiva
        con.execute("PRAGMA synchronous = OFF;")
        con.execute("PRAGMA journal_mode = MEMORY;")
        con.execute("PRAGMA cache_size = 100000;")
        con.execute("PRAGMA temp_store = MEMORY;")

        if clear_existing:
            clear_database_tables(con)

        # 1. Dimensões independentes
        valid_genre_ids = seed_genres(con, data_dir)
        valid_company_ids = seed_companies(con, data_dir)
        valid_person_ids = seed_people(con, data_dir)
        valid_movie_ids = seed_movies(con, data_dir)

        # 2. Tabelas Bridge (relação N:N)
        seed_bridge_movie_genre(con, data_dir, valid_movie_ids, valid_genre_ids)
        seed_bridge_movie_company(con, data_dir, valid_movie_ids, valid_company_ids)
        seed_bridge_movie_person(con, data_dir, valid_movie_ids, valid_person_ids)

        # 3. Fatos e avaliações
        seed_fact_performance(con, data_dir, valid_movie_ids)
        seed_dim_reviews(con, data_dir, valid_movie_ids)
        seed_movie_reviews(con, data_dir, valid_movie_ids)

        # 4. Verificação de integridade referencial
        logger.info("Verificando integridade das chaves estrangeiras...")
        fk_violations = con.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_violations:
            logger.error("Violações de integridade referencial encontradas: %s", fk_violations)
            con.rollback()
            sys.exit(1)
        else:
            logger.info("Integridade referencial confirmada: 0 violações encontradas.")

        # 5. Sumário dos registros inseridos
        logger.info("=== RESUMO DOS REGISTROS NO BANCO DE DADOS ===")
        tables = [
            "dim_genres",
            "dim_companies",
            "dim_people",
            "dim_movies",
            "bridge_movie_genre",
            "bridge_movie_company",
            "bridge_movie_person",
            "fact_movies_performance",
            "dim_reviews",
            "movie_reviews",
        ]
        for t in tables:
            count = con.execute(f"SELECT count(*) FROM {t};").fetchone()[0]
            logger.info("  %-25s: %d registros", t, count)

        total_elapsed = time.time() - start_time
        logger.info("Seed concluído com sucesso em %.2f segundos!", total_elapsed)

    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Povoa o banco de dados rocketlab.db a partir dos arquivos CSV em data/"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Caminho para o diretório de dados contendo os CSVs (padrão: backend/data)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Caminho para o banco de dados SQLite (padrão: backend/rocketlab.db)",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Não limpar os dados existentes antes de realizar o seed",
    )

    args = parser.parse_args()
    run_seed(
        data_dir=args.data_dir,
        db_path=args.db_path,
        clear_existing=not args.no_clear,
    )


if __name__ == "__main__":
    main()
