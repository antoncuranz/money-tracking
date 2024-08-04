import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Check, Clock, Delete, Info, Pencil, Trash, Trash2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";

interface Props {
  exchange: any,
}

const ExchangeRow = ({exchange}: Props) => {

  function isAppliedToPayment() {
    return  exchange["exchangepayment_set"] != null && exchange["exchangepayment_set"].length > 0
  }

  function calculateAppliedAmount() {
    return exchange["exchangepayment_set"].map(ct => ct["amount"]).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow>
      <TableCell>{exchange["date"].substring(0, 16)}</TableCell>
      <TableCell>{exchange["exchange_rate"]}</TableCell>
      <TableCell style={{textAlign: "right"}}>
        { isAppliedToPayment() ?
          <>
            <span className="line-through mr-1">{formatAmount(exchange["amount_usd"])}</span>
            <span style={{color: "green"}}>{formatAmount(exchange["amount_usd"] - calculateAppliedAmount())}</span>
          </>
          : formatAmount(exchange["amount_usd"])
        }
      </TableCell>
      <TableCell style={{textAlign: "right"}}>
        {formatAmount(exchange["amount_eur"])}
      </TableCell>
      <TableCell style={{float: "right"}}>
        <Button variant="outline" size="icon">
          <Pencil className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" className="ml-2" disabled={isAppliedToPayment()}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </TableCell>
    </TableRow>
  )
}

export default ExchangeRow