import type { Genre } from "./genre";

export type PersonType = "Ator" | "Diretor" | "Roteirista";

export interface Person {
  sk_person_id: string;
  nome_pessoa: string;
  tipo_pessoa: PersonType;
}

export interface PeopleListResponse {
  items: Person[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PersonFilters {
  nome_pessoa?: string;
  tipo_pessoa?: string;
  page?: number;
  size?: number;
}

export interface PersonMovie {
  sk_movie_id: string;
  id_filme: string;
  titulo: string;
  ano_lancamento?: number | null;
  url_poster?: string | null;
  genres: Genre[];
  nota_tmdb?: number | null;
  nota_imdb?: number | null;
}

export interface PersonMovieListResponse {
  items: PersonMovie[];
  total: number;
}
