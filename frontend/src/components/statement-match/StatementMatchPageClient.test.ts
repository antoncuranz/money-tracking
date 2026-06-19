import {
  createStatementDraftAmounts,
  getActiveStatementDraftAmounts,
  getMatchedStatementRows,
} from "@/components/statement-match/state.ts";
import {describe, expect, it} from "vitest";

describe("statement-match state helpers", () => {
  const response = {
    account_id: 1,
    results: [
      {
        transaction_id: 11,
        date: "2024-01-01",
        amount_usd: 1000,
        amount_eur: 111,
        guessed_amount_eur: 109,
        counterparty: "One",
        description: "First",
        matched: true,
        confidence: 0.9,
        statement_excerpt: "one",
        reason: "match",
      },
      {
        transaction_id: 22,
        date: "2024-01-02",
        amount_usd: 2000,
        amount_eur: null,
        guessed_amount_eur: 219,
        counterparty: "Two",
        description: "Second",
        matched: false,
        confidence: 0.2,
        statement_excerpt: null,
        reason: "skip",
      },
    ],
  }

  it("keeps only matched backend rows and seeds drafts from amount_eur", () => {
    const rows = getMatchedStatementRows(response)

    expect(rows.map(row => row.transaction_id)).toEqual([11])
    expect(createStatementDraftAmounts(rows)).toEqual({11: 111})
  })

  it("returns only the active tab draft map for saving", () => {
    expect(getActiveStatementDraftAmounts([
      {id: "one", accountId: 1, accountName: "One", fileName: "one.pdf", status: "ready", rows: [], draftAmounts: {11: 111}},
      {id: "two", accountId: 2, accountName: "Two", fileName: "two.pdf", status: "ready", rows: [], draftAmounts: {22: 222}},
    ], "two")).toEqual({22: 222})
  })
})
