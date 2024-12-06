import AmountInput from "@/components/AmountInput.tsx";
import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler} from "react";
import {Account, Transaction} from "@/types.ts";

interface Props {
  transaction: Transaction,
  updateTransactionAmount?: (txId: number, newAmount: number|null) => void,
  onClick: MouseEventHandler<HTMLTableRowElement> | undefined;
  account?: Account,
  readonly?: boolean,
  selectable?: boolean,
}

const TransactionRow = ({transaction, account, updateTransactionAmount, readonly, selectable, onClick}: Props) => {

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
    const classes = ["containers", "border-b"]

    if (selectable)
      classes.push("hover:bg-muted cursor-pointer")

    if (transaction.ignore)
      classes.push("line-through")

    return classes.join(" ")
  }
  return (
    <div onClick={onClick} className={getClasses()} style={{borderLeftWidth: "4px", borderLeftColor: account?.color ?? "transparent", borderLeftStyle: transaction.status == 1 ? "dashed" : "solid"}}>
      <div className="left">
        <div className="date text-sm text-muted-foreground">{transaction.date.substring(0, 16)}</div>
        <div className="remoteName font-medium">{transaction.counterparty}</div>
        <div className="purpose">{transaction.description}</div>
      </div>
      <div className="right">
        <AmountInput className="w-24" amount={transaction.amount_eur} setAmount={updateAmount} disabled={readonly}/>
        <span className="price text-sm">
          { isCreditApplied() ?
            <>
              <span className="line-through mr-1">{formatAmount(transaction.amount_usd)}</span>
              <span style={{color: "green"}}>{formatAmount(transaction.amount_usd - calculateCredit())}</span>
            </>
            : formatAmount(transaction.amount_usd)
          }
        </span>
      </div>
    </div>
  )
}

export default TransactionRow