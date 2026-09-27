from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.movies.models import DimGenre, DimMovie
from app.movies.schemas import MovieCreate, MoviePersonInput, MovieUpdate
from app.people.models import DimPerson


class CRUDMovie:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _resolve_genres(self, nomes: list[str]) -> list[DimGenre]:
        """Resolve os gêneros pelo nome, criando os que ainda não existirem."""
        nomes_validos = list(dict.fromkeys(n.strip() for n in nomes if n and n.strip()))

        if not nomes_validos:
            return []

        existentes = (
            (
                await self.db.execute(
                    select(DimGenre).where(DimGenre.nome_genero.in_(nomes_validos))
                )
            )
            .scalars()
            .all()
        )
        por_nome = {genero.nome_genero: genero for genero in existentes}

        for nome in nomes_validos:
            if nome not in por_nome:
                por_nome[nome] = DimGenre(nome_genero=nome)

        self.db.add_all(por_nome.values())

        return [por_nome[nome] for nome in nomes_validos]

    async def _resolve_people(self, pessoas: list[MoviePersonInput]) -> list[DimPerson]:
        """Resolve as pessoas por nome e papel, criando as que ainda não existirem."""
        if not pessoas:
            return []

        pares = list(
            dict.fromkeys(
                (p.nome_pessoa.strip(), p.tipo_pessoa) for p in pessoas if p.nome_pessoa.strip()
            )
        )
        if not pares:
            return []

        nomes = {nome for nome, _ in pares}
        existentes = (
            (await self.db.execute(select(DimPerson).where(DimPerson.nome_pessoa.in_(nomes))))
            .scalars()
            .all()
        )
        por_par = {(p.nome_pessoa, p.tipo_pessoa): p for p in existentes}

        for nome, tipo in pares:
            if (nome, tipo) not in por_par:
                por_par[(nome, tipo)] = DimPerson(nome_pessoa=nome, tipo_pessoa=tipo)

        self.db.add_all(por_par.values())

        return [por_par[par] for par in pares]

    async def create_movie(self, movie: MovieCreate) -> DimMovie:
        movie_data = movie.model_dump(exclude={"genres", "pessoas"})

        if not movie_data.get("id_filme"):
            movie_data["id_filme"] = f"mov_{uuid4().hex[:12]}"

        if movie_data.get("url_poster"):
            movie_data["url_poster"] = str(movie_data["url_poster"])
        if movie_data.get("url_backdrop"):
            movie_data["url_backdrop"] = str(movie_data["url_backdrop"])

        db_movie = DimMovie(**movie_data)
        db_movie.genres = await self._resolve_genres(movie.genres)
        db_movie.people = await self._resolve_people(movie.pessoas)

        self.db.add(db_movie)
        await self.db.commit()

        return await self.get_movie_by_id_filme(movie_data["id_filme"], load_relations=True)

    async def get_movie_by_id_filme(
        self, id_filme: str, load_relations: bool = False
    ) -> DimMovie | None:
        """Busca o filme pelo identificador de negócio id_filme."""
        query = select(DimMovie).where(DimMovie.id_filme == id_filme)
        query = query.options(selectinload(DimMovie.genres))
        if load_relations:
            query = query.options(
                selectinload(DimMovie.people),
                selectinload(DimMovie.performance),
                selectinload(DimMovie.reviews_summary),
            )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_movie_by_sk(self, sk_movie_id: str) -> DimMovie | None:
        """Busca pela surrogate key (chave primária interna)."""
        return await self.db.get(DimMovie, sk_movie_id)

    async def list_movies(
        self,
        *,
        titulo: str | None = None,
        ano: int | None = None,
        genero: str | None = None,
        status_filme: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DimMovie], int]:
        """Lista filmes com busca por nome, múltiplos filtros e paginação."""
        query = select(DimMovie)

        # 1. Filtro de busca por nome (case-insensitive com ILIKE / LIKE)
        if titulo and titulo.strip():
            query = query.where(DimMovie.titulo.ilike(f"%{titulo.strip()}%"))

        # 2. Filtro por ano de lançamento
        if ano is not None:
            query = query.where(DimMovie.ano_lancamento == ano)

        # 3. Filtro por status do filme
        if status_filme and status_filme.strip():
            query = query.where(DimMovie.status_filme.ilike(f"%{status_filme.strip()}%"))

        # 4. Filtro por gênero (faz join com DimGenre)
        if genero and genero.strip():
            query = query.join(DimMovie.genres).where(
                DimGenre.nome_genero.ilike(f"%{genero.strip()}%")
            )
            # Um filme pode ter vários gêneros atendimento ao filtro, então o
            # distinct evita linhas duplicadas no resultado e na contagem.
            query = query.distinct()

        # Calcula o total de registros considerando os mesmos filtros aplicados
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        # Aplica ordenação padrão e paginação
        paged_query = (
            query
            .options(
                selectinload(DimMovie.genres),
                # `pessoas` precisa ser carregado aqui: a resposta inclui o
                # elenco e o lazy load não funciona em sessão assíncrona.
                selectinload(DimMovie.people),
                selectinload(DimMovie.reviews_summary),
            )
            .order_by(
                DimMovie.ano_lancamento.desc().nullslast(), 
                DimMovie.titulo.asc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(paged_query)
        movies = list(result.scalars().all())

        return movies, total

    async def update_movie(self, id_filme: str, movie: MovieUpdate) -> DimMovie | None:
        # As coleções precisam estar carregadas: reatribuí-las exige ler o
        # estado atual, o que dispara lazy load (proibido em async).
        db_movie = await self.get_movie_by_id_filme(id_filme, load_relations=True)
        if db_movie is None:
            return None

        update_data = movie.model_dump(exclude_unset=True, exclude={"genres", "pessoas"})
        for field, value in update_data.items():
            if field in ("url_poster", "url_backdrop") and value is not None:
                value = str(value)
            setattr(db_movie, field, value)

        if movie.genres is not None:
            db_movie.genres = await self._resolve_genres(movie.genres)

        if movie.pessoas is not None:
            db_movie.people = await self._resolve_people(movie.pessoas)

        await self.db.commit()

        return await self.get_movie_by_id_filme(id_filme, load_relations=True)

    async def delete_movie(self, id_filme: str) -> DimMovie | None:
        db_movie = await self.get_movie_by_id_filme(id_filme)
        if db_movie is None:
            return None

        await self.db.delete(db_movie)
        await self.db.commit()
        return db_movie
