import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Cable, Trash2, Undo2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {Exchange} from "@/types.ts";

interface Props {
  exchange: Exchange,
  selected: boolean,
  disabled: boolean,
  selectExchange: () => void,
  unselectExchange: () => void,
  deleteExchange: () => void,
}

const ExchangeRow = ({exchange, selected, disabled, selectExchange, unselectExchange, deleteExchange}: Props) => {

  function isAppliedToPayment() {
    return  exchange.exchangepayment_set != null && exchange.exchangepayment_set.length > 0
  }

  function calculateAppliedAmount() {
    return exchange.exchangepayment_set.map(ep => ep.amount).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow>
      <TableCell>{exchange.date.substring(0, 16)}</TableCell>
      <TableCell>{exchange.exchange_rate}</TableCell>
      <TableCell className="text-right">
        { isAppliedToPayment() ?
          <>
            <span className="line-through mr-1">{formatAmount(exchange.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(exchange.amount_usd - calculateAppliedAmount())}</span>
          </>
          : formatAmount(exchange.amount_usd)
        }
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(exchange.amount_eur)}
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(exchange.paid_eur)}
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(exchange.fees_eur)}
      </TableCell>
      <TableCell className="float-right pt-1.5 pb-0">
        { selected ?
          <Button variant="outline" size="icon" onClick={unselectExchange}>
            <Undo2 className="h-4 w-4" />
          </Button>
          :
          <Button variant="outline" size="icon" disabled={disabled} onClick={selectExchange}>
            <Cable className="h-4 w-4" />
          </Button>
        }
        <Button variant="outline" size="icon" className="ml-2" disabled={disabled || isAppliedToPayment()} onClick={deleteExchange}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </TableCell>
    </TableRow>
  )
}

export default ExchangeRow