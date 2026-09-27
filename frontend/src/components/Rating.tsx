interface RatingProps {
  /** Nota exibida, na escala de 0 a `max` estrelas (0, 0.5, 1, 1.5 ... 5). */
  value: number;
  /** Quantidade de estrelas desenhadas (padrão 5). */
  max?: number;
  /** Quando definido, o componente vira um campo de seleção de nota. */
  onChange?: (value: number) => void;
}

const FILLED = "★";
const HALF = "⯪";
const EMPTY = "☆";

/** Cada estrela pode ser cheia ou meio preenchida. */
const MEIA_ESTRELA = 0.5;
const TOLERANCIA = 0.01;

export function Rating({ value, max = 5, onChange }: RatingProps) {
  const safeValue = Number.isFinite(value) ? Math.min(max, Math.max(0, value)) : 0;

  if (onChange) {
    return <RatingInput value={safeValue} max={max} onChange={onChange} />;
  }

  // A média vinda do banco tem decimais livres (2,365 por exemplo), então as
  // estrelas são desenhadas na meia estrela mais próxima. O número exibido ao
  // lado continua mostrando o valor exato.
  const meioPasso = Math.round(safeValue / MEIA_ESTRELA) * MEIA_ESTRELA;
  const inteiras = Math.floor(meioPasso);
  const meiaEstrela = meioPasso - inteiras >= MEIA_ESTRELA;
  const vazias = Math.max(0, max - inteiras - (meiaEstrela ? 1 : 0));

  return (
    <span
      className="rating"
      role="img"
      aria-label={`${safeValue.toFixed(1)} de ${max} estrelas`}
    >
      {FILLED.repeat(Math.max(0, Math.min(max, inteiras)))}
      {meiaEstrela && HALF}
      {EMPTY.repeat(vazias)}
    </span>
  );
}

function RatingInput({
  value,
  max,
  onChange,
}: {
  value: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="rating rating-input" role="radiogroup" aria-label="Sua nota">
      {Array.from({ length: max }, (_, index) => {
        const notaCheia = index + 1;
        const notaMeia = notaCheia - MEIA_ESTRELA;

        // Metade esquerda da estrela = meia nota, metade direita = nota cheia.
        const selecionar = (event: React.MouseEvent<HTMLButtonElement>) => {
          const caixa = event.currentTarget.getBoundingClientRect();
          const naEsquerda = event.clientX - caixa.left < caixa.width / 2;
          onChange(naEsquerda ? notaMeia : notaCheia);
        };

        const preenchimento =
          value >= notaCheia - TOLERANCIA ? FILLED : value >= notaMeia - TOLERANCIA ? HALF : EMPTY;

        const meiaSelecionada = Math.abs(value - notaMeia) < TOLERANCIA;
        const selecionada = meiaSelecionada || Math.abs(value - notaCheia) < TOLERANCIA;

        return (
          <span className="star-group" key={notaCheia}>
            {/* Alvo da metade esquerda, sobreposto pela estrela da direita. */}
            <button
              type="button"
              tabIndex={-1}
              aria-hidden
              className="star star-half"
              onClick={selecionar}
            />

            <button
              type="button"
              role="radio"
              aria-checked={selecionada}
              aria-label={`${meiaSelecionada ? notaMeia : notaCheia} de ${max} estrelas`}
              className="star star-full"
              onClick={selecionar}
            >
              {preenchimento}
            </button>
          </span>
        );
      })}
    </div>
  );
}
