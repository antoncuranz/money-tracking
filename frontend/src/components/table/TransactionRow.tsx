import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler} from "react";
import {Account, Transaction} from "@/types.ts";
import AmountInput from "@/components/table/AmountInput.tsx";
import TableRow from "@/components/table/TableRow.tsx";

export default function TransactionRow({
  transaction, account, updateTransactionAmount, readonly, selectable, onClick
}: {
  transaction: Transaction,
  updateTransactionAmount?: (txId: number, newAmount: number|null) => void,
  onClick: MouseEventHandler<HTMLTableRowElement> | undefined;
  account?: Account,
  readonly?: boolean,
  selectable?: boolean,
}) {

  function updateAmount(newAmount: number|null) {
    if (updateTransactionAmount)
      updateTransactionAmount(transaction.id, newAmount)
  }

  function isCreditApplied() {
    return  transaction.credittransaction_set != null && transaction.credittransaction_set.length > 0
  }

  function calculateCredit() {
    return transaction.credittransaction_set.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  function getClasses() {
    const classes = []

    if (selectable)
      classes.push("hover:bg-muted cursor-pointer")

    if (transaction.ignore)
      classes.push("line-through")

    return classes.join(" ")
  }

  return (
    <TableRow onClick={onClick} className={getClasses()} style={{ borderLeftStyle: transaction.status == 1 ? "dashed" : "solid" }} account={account} date={transaction.date} remoteName={transaction.counterparty} purpose={transaction.description}>
      <AmountInput className="w-24" amount={transaction.amount_eur} setAmount={updateAmount} disabled={readonly}/>
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