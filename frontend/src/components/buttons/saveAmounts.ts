import {TransactionAmountMap} from "@/types.ts";

export function getSaveErrorDescription(showPartialSaveWarning: boolean, partialSave: boolean) {
  if (!showPartialSaveWarning || !partialSave)
    return undefined

  return "Some earlier rows may already have been saved."
}

export async function saveTransactionAmounts(
  amounts: TransactionAmountMap,
  onError: (txId: string, partialSave: boolean) => void,
) {
  let savedCount = 0

  for (const [txId, amount] of Object.entries(amounts)) {
    const response = await fetch(
      "/api/transactions/" + txId + (amount != null ? "?amount_eur=" + amount : ""),
      {method: "PUT"},
    )

    if (!response.ok) {
      onError(txId, savedCount > 0)
      return false
    }

    savedCount += 1
  }

  return true
}
