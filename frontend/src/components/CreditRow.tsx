import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Cable, Undo2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {Button} from "@/components/ui/button.tsx";

interface Props {
  credit: Credit,
  selected: boolean,
  disabled: boolean,
  selectCredit: () => void,
  unselectCredit: () => void,
}

const CreditRow = ({credit, selected, disabled, selectCredit, unselectCredit}: Props) => {

  function isCreditApplied() {
    return  credit.credittransaction_set != null && credit.credittransaction_set.length > 0
  }

  function calculateCredit() {
    return credit.credittransaction_set.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow>
      <TableCell>{credit.date.substring(0, 16)}</TableCell>
      <TableCell>{credit.counterparty}</TableCell>
      <TableCell>{credit.description}</TableCell>
      <TableCell>{credit.category}</TableCell>
      <TableCell className="text-right">
        { isCreditApplied() ?
          <>
            <span className="line-through mr-1">{formatAmount(credit.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(credit.amount_usd - calculateCredit())}</span>
          </>
          : formatAmount(credit.amount_usd)
        }
      </TableCell>
      <TableCell className="float-right pt-1.5 pb-0">
        { selected ?
          <Button variant="outline" size="icon" onClick={unselectCredit}>
            <Undo2 className="h-4 w-4" />
          </Button>
        :
          <Button variant="outline" size="icon" disabled={disabled} onClick={selectCredit}>
            <Cable className="h-4 w-4" />
          </Button>
        }
      </TableCell>
    </TableRow>
  )
}

export default CreditRow