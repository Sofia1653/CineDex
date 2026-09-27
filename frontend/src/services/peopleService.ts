import { apiGet, buildQuery } from "./api";
import type { PeopleListResponse, Person, PersonFilters, PersonMovieListResponse } from "../types/person";

export async function getPeople(filters: PersonFilters = {}): Promise<PeopleListResponse> {
  return apiGet<PeopleListResponse>(
    `/people${buildQuery({
      nome_pessoa: filters.nome_pessoa,
      tipo_pessoa: filters.tipo_pessoa,
      page: filters.page,
      size: filters.size,
    })}`
  );
}

export async function getPerson(skPersonId: string): Promise<Person> {
  return apiGet<Person>(`/people/${encodeURIComponent(skPersonId)}`);
}

export async function getPersonMovies(skPersonId: string): Promise<PersonMovieListResponse> {
  return apiGet<PersonMovieListResponse>(`/people/${encodeURIComponent(skPersonId)}/movies`);
}
