interface PaginationProps {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pages, onPageChange }: PaginationProps) {
  if (pages <= 1) {
    return null;
  }

  const current = Math.min(Math.max(page, 1), pages);
  const first = Math.max(1, current - 2);
  const last = Math.min(pages, first + 4);
  const numbers = Array.from({ length: last - first + 1 }, (_, index) => first + index);

  return (
    <nav className="pagination" aria-label="Paginação">
      <button
        type="button"
        className="btn"
        disabled={current === 1}
        onClick={() => onPageChange(current - 1)}
      >
        ← Anterior
      </button>

      {numbers.map((number) => (
        <button
          key={number}
          type="button"
          className={number === current ? "page-number active" : "page-number"}
          aria-current={number === current ? "page" : undefined}
          onClick={() => onPageChange(number)}
        >
          {number}
        </button>
      ))}

      <button
        type="button"
        className="btn"
        disabled={current === pages}
        onClick={() => onPageChange(current + 1)}
      >
        Próxima →
      </button>
    </nav>
  );
}
