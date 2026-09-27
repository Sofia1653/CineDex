export interface Review {
  sk_movie_review_id: string;
  sk_movie_id: string;
  nome: string;
  nota: number;
  comentario: string;
  created_at: string;
}

export interface ReviewPayload {
  nome: string;
  nota: number;
  comentario: string;
}

export interface ReviewListResponse {
  items: Review[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ReviewSummary {
  sk_review_id?: string | null;
  sk_movie_id: string;
  qtd_avaliacoes_usuarios: number;
  nota_media_usuarios?: number | null;
}
