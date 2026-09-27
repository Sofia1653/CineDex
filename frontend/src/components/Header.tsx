import { Link, NavLink, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { SearchBar } from "./SearchBar";

interface HeaderProps {
  onAddMovie: () => void;
}

export function Header({ onAddMovie }: HeaderProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isPeopleSection = location.pathname.startsWith("/people");
  const [term, setTerm] = useState("");

  const field = isPeopleSection ? "nome_pessoa" : "titulo";

  function submitSearch(event: React.FormEvent) {
    event.preventDefault();
    const target = isPeopleSection ? "/people" : "/movies";
    const params = new URLSearchParams();

    if (term.trim()) {
      params.set(field, term.trim());
    }

    navigate(`${target}?${params.toString()}`);
  }

  return (
    <header className="app-header">
      <div className="app-header-top">
        <Link to="/movies" className="brand">
          <span aria-hidden="true">🎬</span> CineDex
        </Link>

        <nav className="app-nav">
          <NavLink to="/movies" className={({ isActive }) => (isActive ? "active" : "")}>
            Catálogo
          </NavLink>
          <NavLink to="/people" className={({ isActive }) => (isActive ? "active" : "")}>
            Pessoas
          </NavLink>
        </nav>

        <button type="button" className="btn btn-primary" onClick={onAddMovie}>
          + Adicionar filme
        </button>
      </div>

      <form className="app-search" onSubmit={submitSearch}>
        <SearchBar
          value={term || searchParams.get(field) || ""}
          onChange={setTerm}
          placeholder={
            isPeopleSection
              ? "Buscar atores, diretores, roteiristas ..."
              : "Buscar filmes, diretores, atores ..."
          }
        />
        <button type="submit" className="btn">
          Buscar
        </button>
      </form>
    </header>
  );
}
