import {Button} from "@/components/ui/button.tsx";
import {Cable, Trash2, Undo2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {Exchange} from "@/types.ts";
import TableRow from "@/components/table/TableRow.tsx";

export default function ExchangeRow({
  exchange, selected, disabled, selectExchange, unselectExchange, deleteExchange
}: {
  exchange: Exchange,
  selected: boolean,
  disabled: boolean,
  selectExchange: () => void,
  unselectExchange: () => void,
  deleteExchange: () => void,
}) {

  function isAppliedToPayment() {
    return  exchange.exchangepayment_set != null && exchange.exchangepayment_set.length > 0
  }

  function calculateAppliedAmount() {
    return exchange.exchangepayment_set.map(ep => ep.amount).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow date={exchange.date} remoteName={exchange.exchange_rate.toString()} purpose={formatAmount(exchange.amount_eur) + " € + " + formatAmount(exchange.fees_eur) + " € fees"}>
      <div>
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
      </div>
      { isAppliedToPayment() ?
        <div className="text-sm">
          <span className="line-through mr-1">{formatAmount(exchange.amount_usd)}</span>
          <span style={{color: "green"}}>{formatAmount(exchange.amount_usd - calculateAppliedAmount())}</span>
        </div>
      :
        <span className="text-sm">{formatAmount(exchange.amount_usd)}</span>
      }
    </TableRow>
  )
}