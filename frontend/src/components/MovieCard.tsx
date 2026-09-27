import { Link } from "react-router-dom";
import { POSTER_FALLBACK } from "./poster";
import type { Movie } from "../types/movie";

interface MovieCardProps {
  movie: Movie;
  onSelect?: (movie: Movie) => void;
}

export function MovieCard({ movie, onSelect }: MovieCardProps) {
  const rating = movie.review_summary?.nota_media_usuarios ?? null;
  const reviewCount = movie.review_summary?.qtd_avaliacoes_usuarios ?? 0;
  const genreNames = movie.genres.map((genre) => genre.nome_genero).join(", ");

  return (
    <div className="movie-card">
      <button type="button" className="movie-card-button" onClick={() => onSelect?.(movie)}>
        <img src={movie.url_poster || POSTER_FALLBACK} alt={`Poster de ${movie.titulo}`} loading="lazy" />

        <div className="movie-info">
          <h3>{movie.titulo}</h3>
          <p className="movie-meta">
            {movie.ano_lancamento ?? "—"}
            {genreNames ? ` · ${genreNames}` : ""}
          </p>

          {rating !== null ? (
            <p className="movie-rating">
              ⭐ {rating.toFixed(1)} <span>({reviewCount})</span>
            </p>
          ) : (
            <p className="movie-rating movie-rating-empty">Sem avaliações</p>
          )}
        </div>
      </button>

      {onSelect && (
        <Link className="btn-link movie-card-link" to={`/movies/${movie.id_filme}`}>
          Ver detalhes
        </Link>
      )}
    </div>
  );
}

export default MovieCard;
