import {hasLargeDeviation} from "@/components/table/transactionRow.ts";
import {describe, expect, it} from "vitest";

describe("hasLargeDeviation", () => {
  it("uses the provided baseline amount", () => {
    expect(hasLargeDeviation(1000, 1030)).toBe(true)
    expect(hasLargeDeviation(1000, 1010)).toBe(false)
    expect(hasLargeDeviation(null, 1030)).toBe(false)
  })

  it("treats zero and null values as non-deviating", () => {
    expect(hasLargeDeviation(0, 100)).toBe(false)
    expect(hasLargeDeviation(1000, null)).toBe(false)
  })
})
