import {StatementMatchResponse, StatementMatchResult, StatementMatchTab, TransactionAmountMap} from "@/types.ts";

export function getMatchedStatementRows(response: StatementMatchResponse): StatementMatchResult[] {
  return response.results.filter(result => result.matched)
}

export function createStatementDraftAmounts(rows: StatementMatchResult[]): TransactionAmountMap {
  return Object.fromEntries(
    rows
      .filter(row => row.amount_eur != null)
      .map(row => [row.transaction_id, row.amount_eur]),
  )
}

export function getActiveStatementDraftAmounts(tabs: StatementMatchTab[], activeTabId: string): TransactionAmountMap {
  return tabs.find(tab => tab.id === activeTabId)?.draftAmounts ?? {}
}
