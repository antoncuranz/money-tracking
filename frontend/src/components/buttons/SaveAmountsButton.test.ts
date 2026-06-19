import {getSaveErrorDescription, saveTransactionAmounts} from "@/components/buttons/saveAmounts.ts";
import {beforeEach, describe, expect, it, vi} from "vitest";

describe("saveTransactionAmounts", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("saves sequentially and stops on first failure", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ok: true})
      .mockResolvedValueOnce({ok: false})
      .mockResolvedValueOnce({ok: true})
    vi.stubGlobal("fetch", fetchMock)

    const result = await saveTransactionAmounts({3: 300, 1: 100, 2: 200}, vi.fn())

    expect(result).toBe(false)
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      "/api/transactions/1?amount_eur=100",
      "/api/transactions/2?amount_eur=200",
    ])
  })

  it("calls the error handler with partial-save state", async () => {
    const onError = vi.fn()
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce({ok: true})
      .mockResolvedValueOnce({ok: false}))

    await saveTransactionAmounts({1: 100, 2: 200}, onError)

    expect(onError).toHaveBeenCalledWith("2", true)
  })

  it("keeps the partial-save warning optional", () => {
    expect(getSaveErrorDescription(true, true)).toBe("Some earlier rows may already have been saved.")
    expect(getSaveErrorDescription(true, false)).toBeUndefined()
    expect(getSaveErrorDescription(false, true)).toBeUndefined()
  })
})
