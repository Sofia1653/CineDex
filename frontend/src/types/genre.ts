export interface Genre {
  sk_genre_id: string;
  nome_genero: string;
}

export interface GenreListItem extends Genre {
  qtd_filmes: number;
}

export interface GenreListResponse {
  items: GenreListItem[];
  total: number;
}
