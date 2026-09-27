import { apiGet, apiSend, buildQuery } from "./api";
import type { Review, ReviewListResponse, ReviewPayload, ReviewSummary } from "../types/review";

export async function getReviews(
  skMovieId: string,
  page: number = 1,
  size: number = 50
): Promise<ReviewListResponse> {
  return apiGet<ReviewListResponse>(
    `/reviews/${encodeURIComponent(skMovieId)}/reviews${buildQuery({ page, size })}`
  );
}

export async function createReview(skMovieId: string, review: ReviewPayload): Promise<Review> {
  return apiSend<Review>(`/reviews/${encodeURIComponent(skMovieId)}`, "POST", review);
}

export async function updateReview(
  skMovieReviewId: string,
  review: ReviewPayload
): Promise<Review> {
  return apiSend<Review>(`/reviews/${encodeURIComponent(skMovieReviewId)}`, "PUT", review);
}

export async function deleteReview(skMovieReviewId: string): Promise<void> {
  return apiSend<void>(`/reviews/${encodeURIComponent(skMovieReviewId)}`, "DELETE");
}

export async function getReviewSummary(skMovieId: string): Promise<ReviewSummary> {
  return apiGet<ReviewSummary>(`/reviews/${encodeURIComponent(skMovieId)}/summary`);
}
