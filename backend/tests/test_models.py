from app.db.base import Base
from app.movies import models  # noqa: F401  Registra os modelos ORM.


def test_movie_schema_registers_expected_tables() -> None:
    expected_tables = {
        "bridge_movie_company",
        "bridge_movie_genre",
        "bridge_movie_person",
        "dim_companies",
        "dim_genres",
        "dim_movies",
        "dim_people",
        "dim_reviews",
        "fact_movies_performance",
        "movie_reviews",
    }

    assert set(Base.metadata.tables) == expected_tables
    assert "idioma_original" not in Base.metadata.tables["dim_movies"].columns


def test_movie_review_columns_match_shared_csv() -> None:
    table = Base.metadata.tables["movie_reviews"]

    assert {"sk_movie_review_id", "sk_movie_id", "nome", "nota", "comentario"} <= set(
        table.columns.keys()
    )
    assert table.primary_key.columns.keys() == ["sk_movie_review_id"]


def test_people_columns_match_shared_csv() -> None:
    from app.people.models import DimPerson, bridge_movie_person

    people_table = Base.metadata.tables["dim_people"]
    assert {"sk_person_id", "nome_pessoa", "tipo_pessoa"} <= set(people_table.columns.keys())
    assert people_table.primary_key.columns.keys() == ["sk_person_id"]
    assert DimPerson.__tablename__ == "dim_people"

    bridge_table = Base.metadata.tables["bridge_movie_person"]
    assert {"sk_movie_id", "sk_person_id"} <= set(bridge_table.columns.keys())
    assert set(bridge_table.primary_key.columns.keys()) == {"sk_movie_id", "sk_person_id"}
    assert bridge_movie_person.name == "bridge_movie_person"


def test_reviews_columns_match_shared_csv() -> None:
    from app.reviews.models import DimReview, MovieReview

    dim_reviews_table = Base.metadata.tables["dim_reviews"]
    assert {
        "sk_review_id",
        "sk_movie_id",
        "qtd_avaliacoes_usuarios",
        "nota_media_usuarios",
    } <= set(dim_reviews_table.columns.keys())
    assert dim_reviews_table.primary_key.columns.keys() == ["sk_review_id"]
    assert DimReview.__tablename__ == "dim_reviews"

    movie_reviews_table = Base.metadata.tables["movie_reviews"]
    assert MovieReview.__tablename__ == "movie_reviews"
    assert movie_reviews_table.primary_key.columns.keys() == ["sk_movie_review_id"]

