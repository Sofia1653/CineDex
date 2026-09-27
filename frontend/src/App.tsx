import { useState } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes, useOutletContext } from "react-router-dom";
import { Header } from "./components/Header";
import { AddMovies } from "./pages/AddMovies";
import { MovieDetails } from "./pages/MovieDetails";
import { Movies } from "./pages/Movies";
import { People } from "./pages/People";
import { PersonDetails } from "./pages/Person";
import "./App.css";

/** Injetado nas pages pelo <Outlet context> para reagirem a mudanças do catálogo. */
export interface LayoutOutlet {
  movieListVersion: number;
}

function Layout() {
  const [movieListVersion, setMovieListVersion] = useState(0);
  const [formOpen, setFormOpen] = useState(false);

  return (
    <div className="app">
      <Header onAddMovie={() => setFormOpen(true)} />

      <main className="app-main">
        <Outlet context={{ movieListVersion } satisfies LayoutOutlet} />
      </main>

      <AddMovies
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSaved={() => setMovieListVersion((version) => version + 1)}
      />
    </div>
  );
}

function MoviesRoute() {
  const { movieListVersion } = useOutletContext<LayoutOutlet>();
  return <Movies key={movieListVersion} />;
}

function MovieDetailsRoute() {
  const { movieListVersion } = useOutletContext<LayoutOutlet>();
  return <MovieDetails key={movieListVersion} />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/movies" replace />} />
          <Route path="/movies" element={<MoviesRoute />} />
          <Route path="/movies/:idFilme" element={<MovieDetailsRoute />} />
          <Route path="/people" element={<People />} />
          <Route path="/people/:skPersonId" element={<PersonDetails />} />
          <Route path="*" element={<Navigate to="/movies" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
