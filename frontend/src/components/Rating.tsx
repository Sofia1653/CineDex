interface RatingProps {
  /** Nota exibida. A escala do backend é 0 a 10. */
  value: number;
  /** Quantidade de estrelas desenhadas (padrão 5). */
  max?: number;
  /** Quando definido, o componente vira um campo de seleção de nota. */
  onChange?: (value: number) => void;
}

const FILLED = "★";
const EMPTY = "☆";

export function Rating({ value, max = 5, onChange }: RatingProps) {
  const safeValue = Number.isFinite(value) ? value : 0;
  const filled = Math.round((safeValue / 10) * max);

  if (!onChange) {
    return (
      <span className="rating" aria-label={`${safeValue.toFixed(1)} de 10`}>
        {FILLED.repeat(Math.max(0, Math.min(max, filled)))}
        {EMPTY.repeat(Math.max(0, max - Math.max(0, Math.min(max, filled))))}
      </span>
    );
  }

  return (
    <div className="rating rating-input" role="radiogroup" aria-label="Sua nota">
      {Array.from({ length: max }, (_, index) => {
        const nota = ((index + 1) / max) * 10;

        return (
          <button
            key={nota}
            type="button"
            role="radio"
            aria-checked={safeValue === nota}
            aria-label={`${index + 1} de ${max} estrelas`}
            className={index < filled ? "star star-filled" : "star"}
            onClick={() => onChange(nota)}
          >
            {index < filled ? FILLED : EMPTY}
          </button>
        );
      })}
    </div>
  );
}
