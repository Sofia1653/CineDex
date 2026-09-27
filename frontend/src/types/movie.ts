import type { Genre } from "./genre";
import type { Person } from "./person";
import type { ReviewSummary } from "./review";

export type PersonRole = "Ator" | "Diretor" | "Roteirista";

export interface Movie {
  sk_movie_id: string;
  id_filme: string;
  titulo: string;
  data_lancamento?: string | null;
  ano_lancamento?: number | null;
  duracao_minutos?: number | null;
  status_filme?: string | null;
  sinopse?: string | null;
  url_poster?: string | null;
  url_backdrop?: string | null;
  genres: Genre[];
  pessoas: Person[];
  review_summary: ReviewSummary | null;
}

export interface MovieListResponse {
  items: Movie[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface MoviePayload {
  titulo: string;
  data_lancamento?: string | null;
  ano_lancamento?: number | null;
  duracao_minutos?: number | null;
  status_filme?: string | null;
  sinopse?: string | null;
  url_poster?: string | null;
  url_backdrop?: string | null;
  genres?: string[];
  pessoas?: { nome_pessoa: string; tipo_pessoa: PersonRole }[];
}

export interface MovieFilters {
  titulo?: string;
  ano?: number;
  genero?: string;
  status_filme?: string;
  page?: number;
  size?: number;
}
