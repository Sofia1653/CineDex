import { MovieCard } from "./MovieCard";
import type { Movie } from "../types/movie";

interface MovieGridProps {
  movies: Movie[];
  onSelect?: (movie: Movie) => void;
}

export function MovieGrid({ movies, onSelect }: MovieGridProps) {
  if (movies.length === 0) {
    return <p className="empty-state">Nenhum filme encontrado com esses filtros.</p>;
  }

  return (
    <div className="movie-grid">
      {movies.map((movie) => (
        <MovieCard key={movie.sk_movie_id} movie={movie} onSelect={onSelect} />
      ))}
    </div>
  );
}
