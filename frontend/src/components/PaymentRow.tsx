import {TableCell, TableHead, TableRow} from "@/components/ui/table.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Check, Clock, DraftingCompass, Info, Pencil, Trash, Trash2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";

interface Props {
  payment: any,
  showAccount?: boolean,
}

const PaymentRow = ({payment, showAccount=false}: Props) => {

  function isAppliedToExchange() {
    return  payment["exchangepayment_set"] != null && payment["exchangepayment_set"].length > 0
  }

  function calculateAppliedAmount() {
    return payment["exchangepayment_set"].map(ct => ct["amount"]).reduce((a, b) => a + b, 0)
  }

  function isProcessButtonDisabled() {
    return payment["processed"] || (payment["amount_usd"] - calculateAppliedAmount() != 0)
  }

  return (
    <TableRow>
      <TableCell>{payment["date"].substring(0, 16)}</TableCell>
      { showAccount &&
        <TableCell>{payment["account_id"]}</TableCell>
      }
      <TableCell>{payment["counterparty"]}</TableCell>
      <TableCell>{payment["description"]}</TableCell>
      <TableCell>{payment["category"]}</TableCell>
      <TableCell style={{textAlign: "right"}}>
        { isAppliedToExchange() ?
          <>
            <span className="line-through mr-1">{formatAmount(payment["amount_usd"])}</span>
            <span style={{color: "green"}}>{formatAmount(payment["amount_usd"] - calculateAppliedAmount())}</span>
          </>
          : formatAmount(payment["amount_usd"])
      }
      </TableCell>
      <TableCell style={{textAlign: "right"}}>
        {formatAmount(payment["amount_eur"])}
      </TableCell>
      <TableCell style={{float: "right"}}>
        <Button variant="outline" size="icon" className="ml-2" disabled={isProcessButtonDisabled()}>
          { payment["processed"] ?
            <Check className="h-4 w-4" />
          :
            <DraftingCompass className="h-4 w-4"/>
          }
        </Button>
      </TableCell>
    </TableRow>
  )
}

export default PaymentRow