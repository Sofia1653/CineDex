/**
 * Conversão entre a escala do banco e a escala das estrelas.
 *
 * O `nota_media_usuarios`, o `nota` das resenhas e as notas de IMDb/TMDB chegam do
 * backend na escala de 0 a 10. A interface trabalha com estrelas de 0 a 5, em
 * passos de meia estrela (0, 0,5, 1, 1,5 ... 5), então a conversão acontece só
 * nas bordas: na leitura, para desenhar as estrelas; na escrita, para enviar a
 * nota de volta.
 */

export const NOTA_MAXIMA = 10;
export const ESTRELAS_MAXIMAS = 5;

/** Nota do backend (0 a 10) vira estrelas (0 a 5). */
export function notaParaEstrelas(nota: number | null | undefined): number {
  if (nota === null || nota === undefined || !Number.isFinite(nota)) {
    return 0;
  }

  return clamp(nota / (NOTA_MAXIMA / ESTRELAS_MAXIMAS), 0, ESTRELAS_MAXIMAS);
}

/** Estrelas (0 a 5) vira nota do backend (0 a 10). */
export function estrelasParaNota(estrelas: number): number {
  if (!Number.isFinite(estrelas)) {
    return 0;
  }

  return clamp(estrelas * (NOTA_MAXIMA / ESTRELAS_MAXIMAS), 0, NOTA_MAXIMA);
}

/** Texto curto da nota já em estrelas, como "2" ou "2.5". */
export function formatarEstrelas(nota: number | null | undefined): string {
  return notaParaEstrelas(nota).toFixed(1);
}

function clamp(valor: number, minimo: number, maximo: number): number {
  return Math.min(maximo, Math.max(minimo, valor));
}
