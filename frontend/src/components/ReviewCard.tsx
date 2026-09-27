import { Rating } from "./Rating";
import { formatarEstrelas, notaParaEstrelas } from "../utils/nota";
import type { Review } from "../types/review";

interface ReviewCardProps {
  review: Review;
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
}

export function ReviewCard({ review, onEdit, onDelete }: ReviewCardProps) {
  return (
    <article className="review-card">
      <header>
        <h3>{review.nome}</h3>
        <Rating value={notaParaEstrelas(review.nota)} />
        <span className="muted">{formatarEstrelas(review.nota)}</span>
      </header>

      <p>{review.comentario || "Sem comentário."}</p>

      <footer>
        <time dateTime={review.created_at}>
          {new Date(review.created_at).toLocaleDateString("pt-BR")}
        </time>

        {(onEdit || onDelete) && (
          <div className="review-actions">
            {onEdit && (
              <button type="button" className="btn-link" onClick={() => onEdit(review)}>
                Editar
              </button>
            )}
            {onDelete && (
              <button type="button" className="btn-link" onClick={() => onDelete(review)}>
                Remover
              </button>
            )}
          </div>
        )}
      </footer>
    </article>
  );
}
