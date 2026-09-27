import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { MovieGrid } from "../components/MovieGrid";
import { MoviePreview } from "../components/MoviePreview";
import { Pagination } from "../components/Pagination";
import { useFetch } from "../hooks/useFetch";
import { getGenres } from "../services/genreService";
import { getMovieStatuses, getMovies } from "../services/movieService";
import type { Movie, MovieStatus } from "../types/movie";
import type { GenreListItem } from "../types/genre";

const PAGE_SIZE = 24;
const ANO_MIN = 1800;
const ANO_MAX = 2100;

function parseAno(value: string): number | null {
  const trimmed = value.trim();

  if (trimmed === "" || !/^\d+$/.test(trimmed)) {
    return null;
  }

  const parsed = Number.parseInt(trimmed, 10);
  return parsed >= ANO_MIN && parsed <= ANO_MAX ? parsed : null;
}

export function Movies() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [preview, setPreview] = useState<Movie | null>(null);

  const titulo = searchParams.get("titulo") ?? "";
  const ano = searchParams.get("ano") ?? "";
  const genero = searchParams.get("genero") ?? "";
  const status = searchParams.get("status_filme") ?? "";
  const page = Number.parseInt(searchParams.get("page") ?? "1", 10) || 1;

  // O campo de ano é controlado localmente: enquanto o ano não está completo o
  // valor não pode ir para a URL, senão o input voltaria a um estado vazio a cada
  // tecla digitada.
  const [anoDigitado, setAnoDigitado] = useState(ano);
  const [anoAplicado, setAnoAplicado] = useState(ano);
  const anoInvalido = anoDigitado.trim() !== "" && parseAno(anoDigitado) === null;

  // Navegar pelo histórico do navegador ou limpar os filtros muda o ano da URL,
  // e o campo precisa acompanhar. O ajuste acontece durante a renderização para
  // não gerar um segundo render desnecessário.
  if (ano !== anoAplicado) {
    setAnoAplicado(ano);
    setAnoDigitado(ano);
  }

  const { data: genres } = useFetch<GenreListItem[]>(
    useCallback(() => getGenres().then((response) => response.items), []),
    "genres"
  );

  const { data: statuses } = useFetch<MovieStatus[]>(
    useCallback(() => getMovieStatuses().then((response) => response.items), []),
    "movie-statuses"
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

  function onAnoChange(value: string) {
    setAnoDigitado(value);

    const parsed = parseAno(value);

    if (parsed !== null) {
      applyFilter("ano", String(parsed));
    } else if (value.trim() === "") {
      applyFilter("ano", "");
    }
  }

  function goToPage(next: number) {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(next));
    setSearchParams(params);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function clearFilters() {
    setAnoDigitado("");
    setAnoAplicado("");
    setSearchParams(new URLSearchParams());
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
          Título
          <input
            type="search"
            placeholder="Todos"
            value={titulo}
            onChange={(event) => applyFilter("titulo", event.target.value.trim())}
          />
        </label>

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
            inputMode="numeric"
            min={ANO_MIN}
            max={ANO_MAX}
            placeholder="Todos"
            value={anoDigitado}
            aria-invalid={anoInvalido}
            aria-describedby={anoInvalido ? "ano-erro" : undefined}
            onChange={(event) => onAnoChange(event.target.value)}
          />
        </label>

        <label>
          Status
          <select
            value={status}
            onChange={(event) => applyFilter("status_filme", event.target.value)}
          >
            <option value="">Todos</option>
            {(statuses ?? []).map((item) => (
              <option key={item.nome_status} value={item.nome_status}>
                {item.nome_status} ({item.qtd_filmes})
              </option>
            ))}
          </select>
        </label>

        {hasFilters && (
          <button type="button" className="btn" onClick={clearFilters}>
            Limpar filtros
          </button>
        )}
      </div>

      {anoInvalido && (
        <p className="form-error" id="ano-erro" role="alert">
          Informe um ano entre {ANO_MIN} e {ANO_MAX}, ou deixe em branco para ver todos os filmes.
        </p>
      )}

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
