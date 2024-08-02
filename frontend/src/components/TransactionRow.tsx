import {useEffect, useState} from 'react'
import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Check, Clock} from "lucide-react";
import {useToast} from "@/components/ui/use-toast.ts";

interface Props {
  transaction: any,
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
}

const TransactionRow = ({transaction, updateTransactionAmount, readonly=true}: Props) => {
  const [eurAmount, setEurAmount] = useState("")
  const { toast } = useToast();

  useEffect(() => {
    updateEurAmount()
  }, [transaction["amount_eur"]]);
  function updateEurAmount() {
    setEurAmount(formatAmount(transaction.amount_eur))
  }

  function formatAmount(amount: number|null): string {
    if (!amount) return ""
    const sign = amount < 0 ? "-" : ""
    return sign + Math.abs(amount / 100 >> 0).toString().padStart(1, "0") + "," + Math.abs(amount % 100).toString().padStart(2, "0")
  }

  function onAmountInputChange(txId: string, event: any) {
    if (!updateTransactionAmount) {
      updateEurAmount()
      return;
    }

    const newAmount = event.target.value

    try {
      const newValue = newAmount ? parseMonetaryValue(newAmount) : null
      updateTransactionAmount(txId, newValue)
    } catch (e) {
      toast({title: "Unable to parse amount"})
      updateEurAmount()
    }
  }

  function parseMonetaryValue(valueString: string) {
    const re = /^(-)?(\d*)(?:[.,](\d{0,2}))?\d*$/
    const match = valueString.replace(/\s/g, "").match(re)

    if (!match || match[2].length + (match[3]?.length ?? 0) == 0)
      throw new Error("Unable to parse value string '" + valueString + "'")

    const sign = match[1] ? -1 : 1
    const euros = parseInt(match[2]) || 0
    let cents = parseInt(match[3]) || 0

    if (match[3]?.length == 1)
      cents *= 10

    return sign * (euros * 100 + cents)
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
      <TableCell style={{textAlign: "right"}}>
        {readonly ?
          <>{formatAmount(transaction["amount_eur"])}</>
        :
          <Input value={eurAmount} onChange={e => setEurAmount(e.target.value)} onBlur={e => onAmountInputChange(transaction["id"], e)}
                 style={{textAlign: "right"}}/>
        }
      </TableCell>
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