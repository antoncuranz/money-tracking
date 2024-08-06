export function formatAmount(amount: number|null, decimals = 2): string {
  if (amount == null) return ""
  const sign = amount < 0 ? "-" : ""
  return sign + Math.abs(amount / Math.pow(10, decimals) >> 0).toString().padStart(1, "0") + ","
    + Math.abs(amount % Math.pow(10, decimals)).toString().padStart(decimals, "0")
}
