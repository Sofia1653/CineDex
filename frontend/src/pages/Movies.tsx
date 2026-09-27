import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { MovieGrid } from "../components/MovieGrid";
import { MoviePreview } from "../components/MoviePreview";
import { Pagination } from "../components/Pagination";
import { useFetch } from "../hooks/useFetch";
import { getGenres } from "../services/genreService";
import { getMovies } from "../services/movieService";
import type { Movie } from "../types/movie";
import type { GenreListItem } from "../types/genre";

const PAGE_SIZE = 20;

export function Movies() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [preview, setPreview] = useState<Movie | null>(null);

  const titulo = searchParams.get("titulo") ?? "";
  const ano = searchParams.get("ano") ?? "";
  const genero = searchParams.get("genero") ?? "";
  const status = searchParams.get("status_filme") ?? "";
  const page = Number.parseInt(searchParams.get("page") ?? "1", 10) || 1;

  const { data: genres } = useFetch<GenreListItem[]>(
    useCallback(() => getGenres().then((response) => response.items), []),
    "genres"
  );

  const loadMovies = useCallback(
    () =>
      getMovies({
        titulo: titulo || undefined,
        ano: ano ? Number.parseInt(ano, 10) : undefined,
        genero: genero || undefined,
        status_filme: status || undefined,
        page,
        size: PAGE_SIZE,
      }),
    [titulo, ano, genero, status, page]
  );

  const { data, error, loading } = useFetch(loadMovies, `${titulo}|${ano}|${genero}|${status}|${page}`);

  useEffect(() => {
    document.title = "CineDex · Catálogo";
  }, []);

  function applyFilter(field: string, value: string) {
    const next = new URLSearchParams(searchParams);

    if (value) {
      next.set(field, value);
    } else {
      next.delete(field);
    }

    next.delete("page");
    setSearchParams(next);
  }

  function goToPage(next: number) {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(next));
    setSearchParams(params);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const hasFilters = Boolean(titulo || ano || genero || status);

  return (
    <section className="page">
      <div className="page-head">
        <h1>Catálogo de filmes</h1>
        <p className="muted">
          {loading ? "Carregando..." : `${data?.total ?? 0} filmes encontrados`}
        </p>
      </div>

      <div className="filters">
        <label>
          Gênero
          <select value={genero} onChange={(event) => applyFilter("genero", event.target.value)}>
            <option value="">Todos</option>
            {(genres ?? []).map((genre) => (
              <option key={genre.sk_genre_id} value={genre.nome_genero}>
                {genre.nome_genero} ({genre.qtd_filmes})
              </option>
            ))}
          </select>
        </label>

        <label>
          Ano
          <input
            type="number"
            min="1800"
            max="2100"
            placeholder="Todos"
            value={ano}
            onChange={(event) => applyFilter("ano", event.target.value)}
          />
        </label>

        <label>
          Status
          <select
            value={status}
            onChange={(event) => applyFilter("status_filme", event.target.value)}
          >
            <option value="">Todos</option>
            <option value="Released">Released</option>
            <option value="Post Production">Post Production</option>
            <option value="In Production">In Production</option>
            <option value="Planned">Planned</option>
            <option value="Rumored">Rumored</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </label>

        {hasFilters && (
          <button
            type="button"
            className="btn"
            onClick={() => setSearchParams(new URLSearchParams())}
          >
            Limpar filtros
          </button>
        )}
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <p className="empty-state">Carregando filmes...</p>
      ) : (
        <MovieGrid movies={data?.items ?? []} onSelect={setPreview} />
      )}

      <Pagination page={data?.page ?? page} pages={data?.pages ?? 1} onPageChange={goToPage} />

      <MoviePreview movie={preview} onClose={() => setPreview(null)} />
    </section>
  );
}

export default Movies;
