import { useCallback, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Pagination } from "../components/Pagination";
import { useFetch } from "../hooks/useFetch";
import { getPeople } from "../services/peopleService";
import { formatPersonName, personInitials } from "../utils/personName";
import type { PeopleListResponse, PersonType } from "../types/person";

const PAGE_SIZE = 20;

const PERSON_TYPES: PersonType[] = ["Ator", "Diretor", "Roteirista"];

const TYPE_LABEL: Record<PersonType, string> = {
  Ator: "Ator",
  Diretor: "Diretor",
  Roteirista: "Roteirista",
};

export function People() {
  const [searchParams, setSearchParams] = useSearchParams();

  const nome = searchParams.get("nome_pessoa") ?? "";
  const tipo = searchParams.get("tipo_pessoa") ?? "";
  const page = Number.parseInt(searchParams.get("page") ?? "1", 10) || 1;

  const loadPeople = useCallback(
    () =>
      getPeople({
        nome_pessoa: nome || undefined,
        tipo_pessoa: tipo || undefined,
        page,
        size: PAGE_SIZE,
      }),
    [nome, tipo, page]
  );

  const { data, error, loading } = useFetch<PeopleListResponse>(loadPeople, `${nome}|${tipo}|${page}`);

  useEffect(() => {
    document.title = "CineDex · Pessoas";
  }, []);

  function applyFilter(field: string, value: string) {
    const next = new URLSearchParams(searchParams);

    if (value) {
      next.set(field, value);
    } else {
      next.delete(field);
    }

    next.delete("page");
    setSearchParams(next);
  }

  function goToPage(next: number) {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(next));
    setSearchParams(params);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const hasFilters = Boolean(nome || tipo);

  return (
    <section className="page">
      <div className="page-head">
        <h1>Pessoas</h1>
        <p className="muted">{loading ? "Carregando..." : `${data?.total ?? 0} pessoas`}</p>
      </div>

      <div className="filters">
        <label>
          Função
          <select value={tipo} onChange={(event) => applyFilter("tipo_pessoa", event.target.value)}>
            <option value="">Todas</option>
            {PERSON_TYPES.map((value) => (
              <option key={value} value={value}>
                {TYPE_LABEL[value]}
              </option>
            ))}
          </select>
        </label>

        {hasFilters && (
          <button
            type="button"
            className="btn"
            onClick={() => setSearchParams(new URLSearchParams())}
          >
            Limpar filtros
          </button>
        )}
      </div>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <p className="empty-state">Carregando pessoas...</p>
      ) : (data?.items.length ?? 0) === 0 ? (
        <p className="empty-state">Nenhuma pessoa encontrada.</p>
      ) : (
        <ul className="people-list">
          {data?.items.map((person) => (
            <li key={person.sk_person_id}>
              <Link to={`/people/${person.sk_person_id}`} className="person-item">
                <span className={`person-avatar person-${person.tipo_pessoa.toLowerCase()}`}>
                  {personInitials(person.nome_pessoa)}
                </span>

                <span className="person-info">
                  <strong>{formatPersonName(person.nome_pessoa)}</strong>
                  <span className="muted">{TYPE_LABEL[person.tipo_pessoa]}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <Pagination page={data?.page ?? page} pages={data?.pages ?? 1} onPageChange={goToPage} />
    </section>
  );
}

export default People;
