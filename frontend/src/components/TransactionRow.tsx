import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Check, Clock} from "lucide-react";
import AmountInput from "@/components/AmountInput.tsx";

interface Props {
  transaction: any,
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
}

const TransactionRow = ({transaction, updateTransactionAmount, readonly=true}: Props) => {

  function formatAmount(amount: number|null): string {
    if (!amount) return ""
    const sign = amount < 0 ? "-" : ""
    return sign + Math.abs(amount / 100 >> 0).toString().padStart(1, "0") + "," + Math.abs(amount % 100).toString().padStart(2, "0")
  }

  function updateAmount(newAmount) {
    if (updateTransactionAmount)
      updateTransactionAmount(transaction["id"], newAmount)
  }

  return (
    <TableRow>
      <TableCell>{transaction["date"].substring(0, 16)}</TableCell>
      <TableCell>{transaction["counterparty"]}</TableCell>
      <TableCell>{transaction["description"]}</TableCell>
      <TableCell>{transaction["category"]}</TableCell>
      <TableCell style={{textAlign: "right"}}>
        {formatAmount(transaction["amount_usd"])}
      </TableCell>
      {transaction["amount_eur"] &&
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