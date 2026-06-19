export function hasLargeDeviation(baselineAmount: number | null | undefined, value: number | null) {
  if (baselineAmount == null || baselineAmount === 0 || value == null)
    return false

  const difference = Math.abs(baselineAmount - value)
  return difference / baselineAmount > 0.02
}
