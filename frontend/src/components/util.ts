export function formatAmount(amount: number|null, decimals = 2): string {
  if (amount == null) return ""
  const sign = amount < 0 ? "-" : ""
  let result = sign + Math.abs(amount / Math.pow(10, decimals) >> 0).toString().padStart(1, "0")
  if (decimals != 0)
    result += "," + Math.abs(amount % Math.pow(10, decimals)).toString().padStart(decimals, "0")
  return result
}

export function titlecase(str: string) {
  return str[0].toUpperCase() + str.substring(1).toLowerCase()
}
