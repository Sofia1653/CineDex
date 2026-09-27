import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AddMovies } from "./AddMovies";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { Rating } from "../components/Rating";
import { ReviewCard } from "../components/ReviewCard";
import { useFetch } from "../hooks/useFetch";
import { deleteMovie, getMovie } from "../services/movieService";
import { createReview, deleteReview, getReviews, updateReview } from "../services/reviewService";
import type { Movie } from "../types/movie";
import type { Person } from "../types/person";
import type { Review, ReviewListResponse, ReviewPayload } from "../types/review";
import { POSTER_FALLBACK } from "../components/poster";

interface DetailsData {
  movie: Movie;
  reviews: ReviewListResponse;
}

function groupByRole(people: Person[]) {
  return {
    Diretor: people.filter((person) => person.tipo_pessoa === "Diretor"),
    Ator: people.filter((person) => person.tipo_pessoa === "Ator"),
    Roteirista: people.filter((person) => person.tipo_pessoa === "Roteirista"),
  };
}

function PersonList({ title, people }: { title: string; people: Person[] }) {
  if (people.length === 0) {
    return null;
  }

  return (
    <p className="detail-line">
      <strong>{title}:</strong>{" "}
      {people.map((person, index) => (
        <span key={person.sk_person_id}>
          {index > 0 && ", "}
          <Link to={`/people/${person.sk_person_id}`}>{person.nome_pessoa}</Link>
        </span>
      ))}
    </p>
  );
}

const EMPTY_REVIEW: ReviewPayload = { nome: "", nota: 0, comentario: "" };

export function MovieDetails() {
  const { idFilme = "" } = useParams();
  const navigate = useNavigate();

  const [editing, setEditing] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [form, setForm] = useState<ReviewPayload>(EMPTY_REVIEW);
  const [editingReview, setEditingReview] = useState<Review | null>(null);
  const [sending, setSending] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [confirmReviewDelete, setConfirmReviewDelete] = useState<Review | null>(null);

  // As avaliações são identificadas pelo sk_movie_id, que só vem no detalhe
  // do filme, então as duas requisições são encadeadas.
  const loadDetails = useCallback(async (): Promise<DetailsData> => {
    const movie = await getMovie(idFilme);
    const reviews = await getReviews(movie.sk_movie_id);
    return { movie, reviews };
  }, [idFilme]);

  const { data, error, loading, reload } = useFetch<DetailsData>(loadDetails, idFilme);

  const movie = data?.movie ?? null;
  const reviews = useMemo(() => data?.reviews.items ?? [], [data]);

  useEffect(() => {
    document.title = movie ? `CineDex · ${movie.titulo}` : "CineDex · Filme";
  }, [movie]);

  function startEditing(review: Review) {
    setEditingReview(review);
    setForm({ nome: review.nome, nota: review.nota, comentario: review.comentario });
    setFormError(null);
  }

  function resetForm() {
    setEditingReview(null);
    setForm(EMPTY_REVIEW);
    setFormError(null);
  }

  async function submitReview(event: React.FormEvent) {
    event.preventDefault();

    if (!movie) {
      return;
    }

    setSending(true);
    setFormError(null);

    const payload: ReviewPayload = { ...form, nome: form.nome.trim() || "Anônimo" };

    try {
      if (editingReview) {
        await updateReview(editingReview.sk_movie_review_id, payload);
      } else {
        await createReview(movie.sk_movie_id, payload);
      }

      resetForm();
      reload();
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "Erro ao enviar a avaliação");
    } finally {
      setSending(false);
    }
  }

  async function removeReview(review: Review) {
    try {
      await deleteReview(review.sk_movie_review_id);
      setConfirmReviewDelete(null);
      reload();
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "Erro ao remover a avaliação");
    }
  }

  async function removeMovie() {
    setDeleting(true);
    setDeleteError(null);

    try {
      await deleteMovie(idFilme);
      navigate("/movies");
    } catch (caught) {
      setDeleteError(caught instanceof Error ? caught.message : "Erro ao remover o filme");
      setConfirmDelete(false);
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return <p className="empty-state">Carregando filme...</p>;
  }

  if (!movie) {
    return (
      <section className="page">
        <p className="form-error">{error ?? "Filme não encontrado"}</p>
        <Link className="btn" to="/movies">
          ← Voltar para o catálogo
        </Link>
      </section>
    );
  }

  const { Diretor, Ator, Roteirista } = groupByRole(movie.pessoas);
  const rating = movie.review_summary?.nota_media_usuarios ?? null;
  const reviewCount = movie.review_summary?.qtd_avaliacoes_usuarios ?? reviews.length;

  return (
    <section className="page">
      <div className="detail-toolbar">
        <Link className="btn" to="/movies">
          ← Voltar
        </Link>

        <div className="detail-toolbar-actions">
          <button type="button" className="btn" onClick={() => setEditing(true)}>
            Editar
          </button>
          <button type="button" className="btn btn-danger" onClick={() => setConfirmDelete(true)}>
            Remover
          </button>
        </div>
      </div>

      <article className="detail">
        <img
          className="detail-poster"
          src={movie.url_poster || POSTER_FALLBACK}
          alt={`Poster de ${movie.titulo}`}
        />

        <div className="detail-info">
          <h1>{movie.titulo}</h1>

          <p className="muted">
            {movie.ano_lancamento ?? "Ano desconhecido"}
            {movie.duracao_minutos ? ` · ${movie.duracao_minutos} min` : ""}
            {movie.status_filme ? ` · ${movie.status_filme}` : ""}
          </p>

          <ul className="tag-list">
            {movie.genres.map((genre) => (
              <li key={genre.sk_genre_id} className="tag">
                {genre.nome_genero}
              </li>
            ))}
          </ul>

          <p className="detail-rating">
            {rating !== null ? (
              <>
                <Rating value={rating} /> <span>{rating.toFixed(1)}</span>{" "}
                <span className="muted">({reviewCount} avaliações)</span>
              </>
            ) : (
              <span className="muted">Sem avaliações</span>
            )}
          </p>

          <PersonList title="Direção" people={Diretor} />
          <PersonList title="Elenco" people={Ator} />
          <PersonList title="Roteiro" people={Roteirista} />

          {movie.sinopse && <p className="detail-synopsis">{movie.sinopse}</p>}
        </div>
      </article>

      <section className="reviews">
        <h2>
          {reviewCount} {reviewCount === 1 ? "avaliação" : "avaliações"}
        </h2>

        <form className="review-form" onSubmit={submitReview}>
          <h3>{editingReview ? "Editar sua avaliação" : "Enviar sua avaliação"}</h3>

          <div className="form-row">
            <label>
              Seu nome
              <input
                type="text"
                value={form.nome}
                maxLength={120}
                onChange={(event) => setForm({ ...form, nome: event.target.value })}
                placeholder="Anônimo"
              />
            </label>

            <div className="review-form-rating">
              <span>Nota</span>
              <Rating value={form.nota} onChange={(nota) => setForm({ ...form, nota })} />
              <span className="muted">({form.nota.toFixed(0)}/10)</span>
            </div>
          </div>

          <label>
            Resenha
            <textarea
              rows={3}
              maxLength={4000}
              value={form.comentario}
              onChange={(event) => setForm({ ...form, comentario: event.target.value })}
              placeholder="O que você achou do filme?"
            />
          </label>

          {formError && <p className="form-error">{formError}</p>}

          <div className="modal-actions">
            {editingReview && (
              <button type="button" className="btn" onClick={resetForm}>
                Cancelar edição
              </button>
            )}
            <button type="submit" className="btn btn-primary" disabled={sending || form.nota === 0}>
              {sending ? "Enviando..." : editingReview ? "Salvar avaliação" : "Avaliar"}
            </button>
          </div>
        </form>

        {reviews.length === 0 ? (
          <p className="empty-state">Nenhuma avaliação ainda. Seja o primeiro a avaliar.</p>
        ) : (
          <div className="review-list">
            {reviews.map((review) => (
              <ReviewCard
                key={review.sk_movie_review_id}
                review={review}
                onEdit={startEditing}
                onDelete={setConfirmReviewDelete}
              />
            ))}
          </div>
        )}
      </section>

      <AddMovies
        open={editing}
        movie={movie}
        onClose={() => setEditing(false)}
        onSaved={() => {
          setEditing(false);
          reload();
        }}
      />

      <ConfirmDialog
        open={confirmDelete}
        title="Remover filme"
        message={`Tem certeza que deseja remover "${movie.titulo}"? Essa ação não pode ser desfeita.`}
        confirmLabel={deleting ? "Removendo..." : "Remover"}
        onConfirm={removeMovie}
        onCancel={() => setConfirmDelete(false)}
      />

      <ConfirmDialog
        open={Boolean(confirmReviewDelete)}
        title="Remover avaliação"
        message="Tem certeza que deseja remover esta avaliação?"
        confirmLabel="Remover"
        onConfirm={() => confirmReviewDelete && removeReview(confirmReviewDelete)}
        onCancel={() => setConfirmReviewDelete(null)}
      />

      {deleteError && <p className="form-error">{deleteError}</p>}
    </section>
  );
}

export default MovieDetails;
