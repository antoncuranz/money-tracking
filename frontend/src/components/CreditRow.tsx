import {Cable, Undo2} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {Button} from "@/components/ui/button.tsx";
import {Account, Credit} from "@/types.ts";

interface Props {
  credit: Credit,
  selected: boolean,
  disabled: boolean,
  selectCredit: () => void,
  unselectCredit: () => void,
  account?: Account
}

const CreditRow = ({credit, account, selected, disabled, selectCredit, unselectCredit}: Props) => {

  function isCreditApplied() {
    return  credit.credittransaction_set != null && credit.credittransaction_set.length > 0
  }

  function calculateCredit() {
    return credit.credittransaction_set.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  return (
    <div className="containers border-b" style={{borderLeftWidth: "4px", borderLeftColor: account?.color ?? "transparent"}}>
      <div className="left">
        <div className="date text-sm text-muted-foreground">{credit.date.substring(0, 16)}</div>
        <div className="remoteName font-medium">{credit.counterparty}</div>
        <div className="purpose">{credit.description}</div>
      </div>
      <div className="right">
        {selected ?
          <Button variant="outline" size="icon" onClick={unselectCredit}>
            <Undo2 className="h-4 w-4"/>
          </Button>
          :
          <Button variant="outline" size="icon" disabled={disabled} onClick={selectCredit}>
            <Cable className="h-4 w-4"/>
          </Button>
        }
        {!isCreditApplied() ?
          <div className="text-sm">
            <span className="line-through mr-1">{formatAmount(credit.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(credit.amount_usd - calculateCredit())}</span>
          </div>
        :
          <span className="text-sm">{formatAmount(credit.amount_usd)}</span>
        }
      </div>
    </div>
  )
}

export default CreditRow