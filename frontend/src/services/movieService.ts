import { apiGet, apiSend, buildQuery } from "./api";
import type {
  Movie,
  MovieFilters,
  MovieListResponse,
  MoviePayload,
  MovieStatusListResponse,
} from "../types/movie";

export async function getMovies(filters: MovieFilters = {}): Promise<MovieListResponse> {
  return apiGet<MovieListResponse>(
    `/movies${buildQuery({
      titulo: filters.titulo,
      ano: filters.ano,
      genero: filters.genero,
      status_filme: filters.status_filme,
      page: filters.page,
      size: filters.size,
    })}`
  );
}

export async function getMovieStatuses(): Promise<MovieStatusListResponse> {
  return apiGet<MovieStatusListResponse>("/movies/status");
}

export async function getMovie(idFilme: string): Promise<Movie> {
  return apiGet<Movie>(`/movies/${encodeURIComponent(idFilme)}`);
}

export async function createMovie(movie: MoviePayload): Promise<Movie> {
  return apiSend<Movie>("/movies", "POST", movie);
}

export async function updateMovie(idFilme: string, movie: MoviePayload): Promise<Movie> {
  return apiSend<Movie>(`/movies/${encodeURIComponent(idFilme)}`, "PUT", movie);
}

export async function deleteMovie(idFilme: string): Promise<void> {
  return apiSend<void>(`/movies/${encodeURIComponent(idFilme)}`, "DELETE");
}
