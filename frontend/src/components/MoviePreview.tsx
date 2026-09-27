import { Link } from "react-router-dom";
import { Modal } from "./Modal";
import { Rating } from "./Rating";
import { POSTER_FALLBACK } from "./poster";
import { formatPersonName } from "../utils/personName";
import { formatarEstrelas, notaParaEstrelas } from "../utils/nota";
import type { Movie } from "../types/movie";
import type { Person } from "../types/person";

interface MoviePreviewProps {
  movie: Movie | null;
  onClose: () => void;
}

function groupByRole(people: Person[]) {
  return {
    Diretor: people.filter((person) => person.tipo_pessoa === "Diretor"),
    Ator: people.filter((person) => person.tipo_pessoa === "Ator"),
    Roteirista: people.filter((person) => person.tipo_pessoa === "Roteirista"),
  };
}

function RoleLine({ title, people, limit }: { title: string; people: Person[]; limit?: number }) {
  if (people.length === 0) {
    return null;
  }

  const shown = limit ? people.slice(0, limit) : people;

  return (
    <p className="preview-line">
      <strong>{title}:</strong>{" "}
      {shown.map((person, index) => (
        <span key={person.sk_person_id}>
          {index > 0 && ", "}
          <Link to={`/people/${person.sk_person_id}`}>{formatPersonName(person.nome_pessoa)}</Link>
        </span>
      ))}
      {limit && people.length > limit && <span> e mais {people.length - limit}</span>}
    </p>
  );
}

export function MoviePreview({ movie, onClose }: MoviePreviewProps) {
  if (!movie) {
    return null;
  }

  const { Diretor, Ator, Roteirista } = groupByRole(movie.pessoas);
  const rating = movie.review_summary?.nota_media_usuarios ?? null;
  const reviewCount = movie.review_summary?.qtd_avaliacoes_usuarios ?? 0;

  return (
    <Modal open title={movie.titulo} onClose={onClose} size="lg">
      <div className="preview">
        <img
          className="preview-poster"
          src={movie.url_poster || POSTER_FALLBACK}
          alt={`Poster de ${movie.titulo}`}
        />

        <div className="preview-info">
          <p className="preview-meta">
            {movie.ano_lancamento ?? "—"}
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

          <p className="preview-rating">
            {rating !== null ? (
              <>
                <Rating value={notaParaEstrelas(rating)} />{" "}
                <span>{formatarEstrelas(rating)}</span>{" "}
                <span className="muted">({reviewCount} avaliações)</span>
              </>
            ) : (
              <span className="muted">Sem avaliações</span>
            )}
          </p>

          <RoleLine title="Direção" people={Diretor} />
          <RoleLine title="Elenco" people={Ator} limit={12} />
          <RoleLine title="Roteiro" people={Roteirista} />

          {movie.sinopse && <p className="preview-synopsis">{movie.sinopse}</p>}
        </div>
      </div>

      <div className="modal-actions">
        <button type="button" className="btn" onClick={onClose}>
          Fechar
        </button>
        <Link className="btn btn-primary" to={`/movies/${movie.id_filme}`} onClick={onClose}>
          Abrir mais
        </Link>
      </div>
    </Modal>
  );
}
