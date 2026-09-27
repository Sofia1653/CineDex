import { useCallback, useState } from "react";
import { Modal } from "../components/Modal";
import { useFetch } from "../hooks/useFetch";
import { getGenres } from "../services/genreService";
import { createMovie, updateMovie } from "../services/movieService";
import type { Movie, MoviePayload, PersonRole } from "../types/movie";
import type { GenreListItem } from "../types/genre";

interface AddMoviesProps {
  open: boolean;
  /** Filme informado = modo de edição. Sem filme = modo de criação. */
  movie?: Movie | null;
  onClose: () => void;
  onSaved: (movie: Movie) => void;
}

interface FormState {
  titulo: string;
  ano_lancamento: string;
  diretor: string;
  roteiristas: string;
  elenco: string;
  generos: string[];
  sinopse: string;
  url_poster: string;
}

const EMPTY_FORM: FormState = {
  titulo: "",
  ano_lancamento: "",
  diretor: "",
  roteiristas: "",
  elenco: "",
  generos: [],
  sinopse: "",
  url_poster: "",
};

function splitNames(value: string): string[] {
  return value
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
}

function toForm(movie: Movie): FormState {
  const namesOf = (role: PersonRole) =>
    movie.pessoas
      .filter((person) => person.tipo_pessoa === role)
      .map((person) => person.nome_pessoa)
      .join(", ");

  return {
    titulo: movie.titulo,
    ano_lancamento: movie.ano_lancamento ? String(movie.ano_lancamento) : "",
    diretor: namesOf("Diretor"),
    roteiristas: namesOf("Roteirista"),
    elenco: namesOf("Ator"),
    generos: movie.genres.map((genre) => genre.nome_genero),
    sinopse: movie.sinopse ?? "",
    url_poster: movie.url_poster ?? "",
  };
}

function MovieForm({ movie, onClose, onSaved }: Omit<AddMoviesProps, "open">) {
  const [form, setForm] = useState<FormState>(() => (movie ? toForm(movie) : EMPTY_FORM));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadGenres = useCallback(() => getGenres().then((response) => response.items), []);
  const { data: genres } = useFetch<GenreListItem[]>(loadGenres, "genres");

  const isEditing = Boolean(movie);

  function update<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function toggleGenre(nome: string) {
    setForm((current) => ({
      ...current,
      generos: current.generos.includes(nome)
        ? current.generos.filter((name) => name !== nome)
        : [...current.generos, nome],
    }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);

    const ano = Number.parseInt(form.ano_lancamento, 10);
    const toPeople = (value: string, role: PersonRole) =>
      splitNames(value).map((nome_pessoa) => ({ nome_pessoa, tipo_pessoa: role }));

    const payload: MoviePayload = {
      titulo: form.titulo.trim(),
      ano_lancamento: Number.isNaN(ano) ? null : ano,
      sinopse: form.sinopse.trim() || null,
      url_poster: form.url_poster.trim() || null,
      genres: form.generos,
      pessoas: [
        ...toPeople(form.diretor, "Diretor"),
        ...toPeople(form.elenco, "Ator"),
        ...toPeople(form.roteiristas, "Roteirista"),
      ],
    };

    try {
      const saved = movie
        ? await updateMovie(movie.id_filme, payload)
        : await createMovie(payload);

      onSaved(saved);
      onClose();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Erro ao salvar o filme");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal
      open
      title={isEditing ? `Editar: ${movie?.titulo}` : "Adicionar filme"}
      onClose={onClose}
      size="lg"
    >
      <form className="movie-form" onSubmit={handleSubmit}>
        <label>
          Título
          <input
            type="text"
            value={form.titulo}
            onChange={(event) => update("titulo", event.target.value)}
            required
          />
        </label>

        <div className="form-row">
          <label>
            Ano de lançamento
            <input
              type="number"
              min="1800"
              max="2100"
              value={form.ano_lancamento}
              onChange={(event) => update("ano_lancamento", event.target.value)}
            />
          </label>

          <label>
            Poster (URL)
            <input
              type="url"
              value={form.url_poster}
              onChange={(event) => update("url_poster", event.target.value)}
              placeholder="https://..."
            />
          </label>
        </div>

        <fieldset>
          <legend>Gêneros</legend>

          {!genres ? (
            <p className="muted">Carregando catálogo de gêneros...</p>
          ) : (
            <div className="genre-options">
              {genres.map((genre) => (
                <label key={genre.sk_genre_id} className="genre-option">
                  <input
                    type="checkbox"
                    checked={form.generos.includes(genre.nome_genero)}
                    onChange={() => toggleGenre(genre.nome_genero)}
                  />
                  {genre.nome_genero}
                </label>
              ))}
            </div>
          )}
        </fieldset>

        <label>
          Diretor(es)
          <input
            type="text"
            value={form.diretor}
            onChange={(event) => update("diretor", event.target.value)}
            placeholder="Separe por vírgula"
          />
        </label>

        <label>
          Elenco
          <input
            type="text"
            value={form.elenco}
            onChange={(event) => update("elenco", event.target.value)}
            placeholder="Separe por vírgula"
          />
        </label>

        <label>
          Roteirista(s)
          <input
            type="text"
            value={form.roteiristas}
            onChange={(event) => update("roteiristas", event.target.value)}
            placeholder="Separe por vírgula"
          />
        </label>

        <label>
          Sinopse
          <textarea
            rows={4}
            value={form.sinopse}
            onChange={(event) => update("sinopse", event.target.value)}
          />
        </label>

        {error && <p className="form-error">{error}</p>}

        <div className="modal-actions">
          <button type="button" className="btn" onClick={onClose}>
            Cancelar
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Salvando..." : "Salvar"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export function AddMovies({ open, movie, onClose, onSaved }: AddMoviesProps) {
  if (!open) {
    return null;
  }

  // A key remonta o formulário a cada abertura, então os campos já vêm
  // preenchidos no modo de edição sem precisar de efeito.
  return (
    <MovieForm
      key={movie?.id_filme ?? "novo"}
      movie={movie}
      onClose={onClose}
      onSaved={onSaved}
    />
  );
}

export default AddMovies;
