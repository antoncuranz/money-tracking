import {Cable, Undo2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {Button} from "@/components/ui/button.tsx";
import {Account, Credit} from "@/types.ts";
import TableRow from "@/components/table/TableRow.tsx";

export default function CreditRow({
  credit, account, selected, disabled, selectCredit, unselectCredit
}: {
  credit: Credit,
  selected: boolean,
  disabled: boolean,
  selectCredit: () => void,
  unselectCredit: () => void,
  account?: Account
}) {

  function isCreditApplied() {
    return  credit.credittransaction_set != null && credit.credittransaction_set.length > 0
  }

  function calculateCredit() {
    return credit.credittransaction_set.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  return (
    <TableRow account={account} date={credit.date} remoteName={credit.counterparty} purpose={credit.description}>
      {selected ?
        <Button variant="outline" size="icon" onClick={unselectCredit}>
          <Undo2 className="h-4 w-4"/>
        </Button>
        :
        <Button variant="outline" size="icon" disabled={disabled} onClick={selectCredit}>
          <Cable className="h-4 w-4"/>
        </Button>
      }
      <span className="price text-sm">
        {isCreditApplied() ?
          <>
            <span className="line-through mr-1">{formatAmount(credit.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(credit.amount_usd - calculateCredit())}</span>
          </>
        :
          formatAmount(credit.amount_usd)
        }
      </span>
    </TableRow>
)
}