import { useCallback, useEffect, useState } from "react";

interface FetchState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

/**
 * Busca dados de API reagindo a `key` (string com os parâmetros da requisição).
 * O estado anterior é descartado comparando a key, então nada de setState
 * síncrono dentro do effect. `fetcher` precisa ser estável (useCallback).
 */
export function useFetch<T>(fetcher: () => Promise<T>, key: string): FetchState<T> {
  const [version, setVersion] = useState(0);
  const [state, setState] = useState<{ key: string; data: T | null; error: string | null }>({
    key,
    data: null,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    fetcher().then(
      (data) => {
        if (!cancelled) {
          setState({ key, data, error: null });
        }
      },
      (caught: Error) => {
        if (!cancelled) {
          setState({ key, data: null, error: caught.message });
        }
      }
    );

    return () => {
      cancelled = true;
    };
  }, [key, fetcher, version]);

  const reload = useCallback(() => setVersion((current) => current + 1), []);
  const loading = state.key !== key;

  return {
    data: loading ? null : state.data,
    error: loading ? null : state.error,
    loading,
    reload,
  };
}
