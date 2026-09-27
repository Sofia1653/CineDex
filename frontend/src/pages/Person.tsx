import { useCallback, useEffect, useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { Rating } from "../components/Rating";
import { useFetch } from "../hooks/useFetch";
import { getPerson, getPersonMovies } from "../services/peopleService";
import { formatPersonName, personInitials } from "../utils/personName";
import { formatarEstrelas, notaParaEstrelas } from "../utils/nota";
import type { Person, PersonMovie, PersonMovieListResponse } from "../types/person";
import { POSTER_FALLBACK } from "../components/poster";

function movieRating(movie: PersonMovie): number | null {
  if (movie.nota_imdb !== null && movie.nota_imdb !== undefined) {
    return movie.nota_imdb;
  }

  if (movie.nota_tmdb !== null && movie.nota_tmdb !== undefined) {
    return movie.nota_tmdb;
  }

  return null;
}

export function PersonDetails() {
  const { skPersonId = "" } = useParams();

  const loadPerson = useCallback(() => getPerson(skPersonId), [skPersonId]);
  const loadMovies = useCallback(
    () => getPersonMovies(skPersonId),
    [skPersonId]
  );

  const { data: person, error, loading } = useFetch<Person>(loadPerson, skPersonId);
  const { data: movieList } = useFetch<PersonMovieListResponse>(loadMovies, skPersonId);

  useEffect(() => {
    document.title = person ? `CineDex · ${formatPersonName(person.nome_pessoa)}` : "CineDex · Pessoa";
  }, [person]);

  const movies = useMemo(() => movieList?.items ?? [], [movieList]);

  const mediaNota = useMemo(() => {
    const notas = movies
      .map(movieRating)
      .filter((nota): nota is number => nota !== null && nota > 0);

    if (notas.length === 0) {
      return null;
    }

    return notas.reduce((total, nota) => total + nota, 0) / notas.length;
  }, [movies]);

  if (loading) {
    return <p className="empty-state">Carregando pessoa...</p>;
  }

  if (!person) {
    return (
      <section className="page">
        <p className="form-error">{error ?? "Pessoa não encontrada"}</p>
        <Link className="btn" to="/people">
          ← Voltar para pessoas
        </Link>
      </section>
    );
  }

  const nome = person ? formatPersonName(person.nome_pessoa) : "";

  return (
    <section className="page">
      <div className="detail-toolbar">
        <Link className="btn" to="/people">
          ← Voltar
        </Link>
      </div>

      <header className="person-header">
        <span className={`person-avatar person-avatar-lg person-${person.tipo_pessoa.toLowerCase()}`}>
          {personInitials(person.nome_pessoa)}
        </span>

        <div>
          <h1>{nome}</h1>
          <p className="muted">{person.tipo_pessoa}</p>

          <ul className="person-stats">
            <li>
              <strong>{movies.length}</strong>
              <span>{movies.length === 1 ? "filme" : "filmes"}</span>
            </li>
            <li>
              <strong>{mediaNota !== null ? formatarEstrelas(mediaNota) : "—"}</strong>
              <span>média das notas</span>
            </li>
          </ul>
        </div>
      </header>

      <h2>Filmografia</h2>

      {movies.length === 0 ? (
        <p className="empty-state">Nenhum filme vinculado a esta pessoa.</p>
      ) : (
        <div className="table-wrapper">
          <table className="person-movies">
            <thead>
              <tr>
                <th>Capa</th>
                <th>Ano</th>
                <th>Filme</th>
                <th>Gênero</th>
                <th>Nota</th>
              </tr>
            </thead>

            <tbody>
              {movies.map((movie) => {
                const nota = movieRating(movie);

                return (
                  <tr key={movie.sk_movie_id}>
                    <td>
                      <img
                        className="person-movie-poster"
                        src={movie.url_poster || POSTER_FALLBACK}
                        alt={`Poster de ${movie.titulo}`}
                        loading="lazy"
                      />
                    </td>
                    <td>{movie.ano_lancamento ?? "—"}</td>
                    <td>
                      <Link to={`/movies/${movie.id_filme}`}>{movie.titulo}</Link>
                    </td>
                    <td>
                      {movie.genres.length > 0
                        ? movie.genres.map((genre) => genre.nome_genero).join(", ")
                        : "—"}
                    </td>
                    <td>
                      {nota !== null ? (
                        <span className="person-movie-rating">
                          <Rating value={notaParaEstrelas(nota)} />
                          {formatarEstrelas(nota)}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default PersonDetails;
