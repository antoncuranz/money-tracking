import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Check, Clock} from "lucide-react";
import AmountInput from "@/components/AmountInput.tsx";
import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler} from "react";

interface Props {
  transaction: any,
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
  selectable?: boolean,
  onClick?: MouseEventHandler<HTMLTableRowElement> | undefined;
}

const TransactionRow = ({transaction, updateTransactionAmount, readonly, selectable, onClick=null}: Props) => {

  function updateAmount(newAmount) {
    if (updateTransactionAmount)
      updateTransactionAmount(transaction["id"], newAmount)
  }

  function isCreditApplied() {
    return  transaction["credittransaction_set"] != null && transaction["credittransaction_set"].length > 0
  }

  function calculateCredit() {
    return transaction["credittransaction_set"].map(ct => ct["amount"]).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow onClick={onClick} className={selectable ? "hover:bg-muted cursor-pointer" : ""}>
      <TableCell>{transaction["date"].substring(0, 16)}</TableCell>
      <TableCell>{transaction["counterparty"]}</TableCell>
      <TableCell>{transaction["description"]}</TableCell>
      <TableCell>{transaction["category"]}</TableCell>
      <TableCell className="text-right">
        { isCreditApplied() ?
          <>
            <span className="line-through mr-1">{formatAmount(transaction["amount_usd"])}</span>
            <span style={{color: "green"}}>{formatAmount(transaction["amount_usd"] - calculateCredit())}</span>
          </>
          : formatAmount(transaction["amount_usd"])
        }
      </TableCell>
      <TableCell className="text-right pt-0 pb-0">
        <AmountInput amount={transaction.amount_eur} setAmount={updateAmount} disabled={readonly}/>
      </TableCell>
      <TableCell>
        {transaction["status"] == 1 &&
            <Clock className="h-5 w-5 float-right"/>
        }
        {transaction["status"] == 3 &&
            <Check className="h-5 w-5 float-right"/>
        }
      </TableCell>
    </TableRow>
  )
}

export default TransactionRow