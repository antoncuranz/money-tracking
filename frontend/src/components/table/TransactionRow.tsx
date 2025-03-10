import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler} from "react";
import {Account, Transaction} from "@/types.ts";
import AmountInput from "@/components/dialog/AmountInput.tsx";
import TableRow from "@/components/table/TableRow.tsx";
import {useStore} from "@/store.ts";

export default function TransactionRow({
  transaction, account, readonly, selectable, onClick
}: {
  transaction: Transaction,
  onClick: MouseEventHandler<HTMLTableRowElement> | undefined;
  account?: Account,
  readonly?: boolean,
  selectable?: boolean,
}) {

  const { putTransactionAmount, clearTransactionAmount } = useStore()

  function isCreditApplied() {
    return  transaction.credits != null && transaction.credits.length > 0
  }

  function calculateCredit() {
    return transaction.credits.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  function getClasses() {
    const classes = []

    if (selectable)
      classes.push("hover:bg-muted cursor-pointer")

    if (transaction.ignore)
      classes.push("line-through")

    return classes.join(" ")
  }

  function largeDeviation(transaction: Transaction, value: number|null) {
    if (!transaction.guessed_amount_eur || value == null)
      return false

    const difference = Math.abs(transaction.guessed_amount_eur - value)
    return difference/transaction.guessed_amount_eur > 0.02
  }

  function updateTransactionAmount(transaction: Transaction, amount: number | null) {
    if (transaction.amount_eur == amount)
      clearTransactionAmount(transaction.id)
    else
      putTransactionAmount(transaction.id, amount)
  }

  return (
    <TableRow onClick={onClick} className={getClasses()} style={{ borderLeftStyle: transaction.status == 1 ? "dashed" : "solid" }} account={account} date={transaction.date} remoteName={transaction.counterparty} purpose={transaction.description}>
      <AmountInput className="w-24 placeholder:opacity-50" amount={transaction.amount_eur} placeholder={formatAmount(transaction.guessed_amount_eur)} updateAmount={amount => updateTransactionAmount(transaction, amount)} disabled={readonly} warnPredicate={amount => largeDeviation(transaction, amount)}/>
      <span className="price text-sm">
        { isCreditApplied() ?
          <>
            <span className="line-through mr-1">{formatAmount(transaction.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(transaction.amount_usd - calculateCredit())}</span>
          </>
        :
          formatAmount(transaction.amount_usd)
        }
      </span>
    </TableRow>
  )
}