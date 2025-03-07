import {Button} from "@/components/ui/button.tsx";
import {Check, DraftingCompass, LoaderCircle} from "lucide-react";
import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler, useState} from "react";
import {Account, Payment} from "@/types.ts";
import TableRow from "@/components/table/TableRow.tsx";

interface Props {
  payment: Payment,
  account?: Account,
  onClick: MouseEventHandler<HTMLTableRowElement> | undefined,
  onProcessPaymentClick: () => void,
  selectable?: boolean,
}

const PaymentRow = ({payment, account, selectable, onClick, onProcessPaymentClick}: Props) => {
  const [inProgress, setInProgress] = useState(false)

  function isAppliedToExchange() {
    return  payment.exchangepayment_set != null && payment.exchangepayment_set.length > 0
  }

  function calculateAppliedAmount() {
    return payment.exchangepayment_set.map(ct => ct.amount).reduce((a, b) => a + b, 0)
  }

  function isProcessButtonDisabled() {
    return inProgress || selectable || payment.status != 2 || (payment.amount_usd - calculateAppliedAmount() != 0)
  }

  async function onProcessPaymentClickLocal() {
    setInProgress(true)
    await onProcessPaymentClick()
    setInProgress(false)
  }

  function getClasses() {
    if (selectable)
      return "hover:bg-muted cursor-pointer"
    else
      return ""
  }

  return (
    <TableRow onClick={onClick} className={getClasses()} style={{ borderLeftStyle: payment.status == 1 ? "dashed" : "solid" }} date={payment.date} remoteName={payment.counterparty} purpose={payment.description} account={account}>
      <span className="flex items-center">
        <span className="text-sm w-18 text-right">{formatAmount(payment.amount_eur)} €</span>
        <Button variant="outline" size="icon" className="ml-2" disabled={isProcessButtonDisabled()}
                onClick={onProcessPaymentClickLocal}>
          {payment.status == 3 ?
            <Check className="h-4 w-4"/>
          :
            (inProgress ?
              <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
            :
              <DraftingCompass className="h-4 w-4"/>
            )
          }
        </Button>
      </span>
      <span className="text-sm ml-2">
        {isAppliedToExchange() ?
          <>
            $ <span className="line-through mr-1">{formatAmount(payment.amount_usd)}</span>
            <span style={{color: "green"}}>{formatAmount(payment.amount_usd - calculateAppliedAmount())}</span>
          </>
        :
          "$ " + formatAmount(payment.amount_usd)
        }
      </span>
    </TableRow>
  )
}

export default PaymentRow