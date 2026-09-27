import { apiGet } from "./api";
import type { GenreListResponse } from "../types/genre";

export async function getGenres(): Promise<GenreListResponse> {
  return apiGet<GenreListResponse>("/genres");
}
