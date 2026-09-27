export const API_URL = "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const FIELD_LABELS: Record<string, string> = {
  query: "Filtro",
  body: "",
  path: "",
  ano: "Ano",
  page: "Página",
  size: "Quantidade por página",
  titulo: "Título",
  genero: "Gênero",
  status_filme: "Status",
  nome: "Nome",
  nota: "Nota",
  comentario: "Comentário",
  nome_pessoa: "Nome da pessoa",
  tipo_pessoa: "Tipo de pessoa",
  url_poster: "URL do pôster",
  url_backdrop: "URL do backdrop",
};

const GENERIC_MESSAGES: Record<string, string> = {
  "Input should be a valid integer": "Informe um número inteiro.",
  "Input should be a valid number": "Informe um número válido.",
  "Input should be a valid string": "Informe um texto.",
  "Field required": "Campo obrigatório.",
  "Value error": "Valor inválido.",
  "Input should be 'Ator', 'Diretor' or 'Roteirista'": "Escolha Ator, Diretor ou Roteirista.",
  "Input should be less than or equal to 10": "A nota deve ser no máximo 10.",
  "Input should be greater than or equal to 0": "A nota deve ser no mínimo 0.",
  "Input should be greater than or equal to 1": "O valor deve ser no mínimo 1.",
};

function fieldLabel(loc: unknown): string | null {
  if (!Array.isArray(loc) || loc.length === 0) {
    return null;
  }

  const field = loc[loc.length - 1];
  return typeof field === "string" ? (FIELD_LABELS[field] ?? field) : null;
}

function friendlyMessage(item: { loc?: unknown[]; msg?: string }): string | null {
  const label = fieldLabel(item.loc);
  const raw = item.msg ?? "";

  if (/greater than or equal to/i.test(raw) || /less than or equal to/i.test(raw)) {
    const bound = raw.match(/(\d+(?:\.\d+)?)/)?.[1];
    const isMin = /greater than or equal to/i.test(raw);
    if (label && bound) {
      return isMin
        ? `${label} deve ser no mínimo ${bound}.`
        : `${label} deve ser no máximo ${bound}.`;
    }
  }

  if (label && GENERIC_MESSAGES[raw]) {
    return GENERIC_MESSAGES[raw];
  }

  if (label && raw === "Field required") {
    return `Informe ${label.toLowerCase()}.`;
  }

  if (label && raw) {
    return `${label}: ${raw.charAt(0).toLowerCase()}${raw.slice(1)}.`;
  }

  return raw || null;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    const detail = body?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const messages = detail
        .map((item: { loc?: unknown[]; msg?: string }) => friendlyMessage(item))
        .filter((message): message is string => Boolean(message));

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    // resposta sem JSON (ex.: 500 do servidor)
  }

  if (response.status === 404) {
    return "Não encontramos o que você procura.";
  }

  if (response.status >= 500) {
    return "O servidor encontrou um problema. Tente novamente em instantes.";
  }

  return "Não foi possível completar a operação. Tente novamente.";
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw new ApiError(await extractErrorMessage(response), response.status);
  }

  return response.json() as Promise<T>;
}

export async function apiSend<T>(
  path: string,
  method: "POST" | "PUT" | "DELETE",
  body?: unknown
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    throw new ApiError(await extractErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function buildQuery(params: Record<string, string | number | undefined>): string {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  });

  const queryString = query.toString();

  return queryString ? `?${queryString}` : "";
}
