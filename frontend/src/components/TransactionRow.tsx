import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Check, Clock} from "lucide-react";
import AmountInput from "@/components/AmountInput.tsx";
import {formatAmount} from "@/components/util.ts";

interface Props {
  transaction: any,
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
  showAmountEur?: boolean,
}

const TransactionRow = ({transaction, updateTransactionAmount, readonly=true, showAmountEur=false}: Props) => {

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
    <TableRow>
      <TableCell>{transaction["date"].substring(0, 16)}</TableCell>
      <TableCell>{transaction["counterparty"]}</TableCell>
      <TableCell>{transaction["description"]}</TableCell>
      <TableCell>{transaction["category"]}</TableCell>
      <TableCell style={{textAlign: "right"}}>
        { isCreditApplied() ?
          <>
            <span className="line-through mr-1">{formatAmount(transaction["amount_usd"])}</span>
            <span style={{color: "green"}}>{formatAmount(transaction["amount_usd"] - calculateCredit())}</span>
          </>
          : formatAmount(transaction["amount_usd"])
        }
      </TableCell>
      { showAmountEur &&
        <TableCell style={{textAlign: "right"}}>
          {readonly ?
            <>{formatAmount(transaction["amount_eur"])}</>
          :
            <AmountInput amount={transaction.amount_eur} setAmount={updateAmount}/>
          }
        </TableCell>
      }
      <TableCell>
        {transaction["status"] == 1 &&
            <Clock className="h-5 w-5" style={{float: "right"}}/>
        }
        {transaction["status"] == 3 &&
            <Check className="h-5 w-5" style={{float: "right"}}/>
        }
      </TableCell>
    </TableRow>
  )
}

export default TransactionRow