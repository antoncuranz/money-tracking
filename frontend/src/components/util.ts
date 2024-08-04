export function formatAmount(amount: number|null): string {
  if (amount == null) return ""
  const sign = amount < 0 ? "-" : ""
  return sign + Math.abs(amount / 100 >> 0).toString().padStart(1, "0") + "," + Math.abs(amount % 100).toString().padStart(2, "0")
}
