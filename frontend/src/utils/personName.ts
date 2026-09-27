const ASPAS = "\"'“”‘’`´";
const DUPLA_ASPAS = /""+/g;
const INICIO_ASPAS = new RegExp(`^[${ASPAS}]+`);
const FIM_ASPAS = /[\s"'“”]+$/;

/**
 * Nomes de pessoas chegam do banco com defeitos do dataset de origem (aspas
 * orfas no início, inicial minúscula, espaços duplicados). A limpeza definitiva
 * acontece na carga do banco, mas o display é normalizado aqui também para que
 * registros antigos continuem legíveis.
 */
export function formatPersonName(nome: string): string {
  const bruto = nome.trim();
  const limpo = bruto
    .replace(DUPLA_ASPAS, '"')
    .replace(INICIO_ASPAS, "")
    .replace(FIM_ASPAS, "")
    .replace(/\s+/g, " ")
    .trim();

  if (!limpo) {
    return bruto;
  }

  // A inicial minúscula do dataset sempre vem junto da aspa de abertura.
  if (ASPAS.includes(bruto.charAt(0))) {
    return limpo.charAt(0).toUpperCase() + limpo.slice(1);
  }

  return limpo;
}

/** Inicial para o avatar: nunca começa com aspa ou espaço. */
export function personInitials(nome: string): string {
  return formatPersonName(nome).charAt(0).toUpperCase() || "?";
}
