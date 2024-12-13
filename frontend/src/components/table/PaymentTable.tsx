"use client"

import {Account, Payment} from "@/types.ts";
import PaymentRow from "@/components/table/PaymentRow.tsx";
import ExchangePaymentDialog from "@/components/dialog/ExchangePaymentDialog.tsx";
import {useState} from "react";
import {useToast} from "@/components/ui/use-toast.ts";
import {useRouter} from "next/navigation";
import {useStore} from "@/store.ts";

export default function PaymentTable({
  payments, accounts
}: {
  payments: Payment[],
  accounts: Account[]
}) {
  const [paymentSelection, setPaymentSelection] = useState<Payment>()
  const [epDialogOpen, setEpDialogOpen] = useState(false)

  const { exchangeSelection } = useStore()
  const { toast } = useToast();
  const router = useRouter();

  function openExchangePaymentDialog(payment: Payment) {
    if (exchangeSelection != null) {
      setPaymentSelection(payment)
      setEpDialogOpen(true)
    }
  }

  function onEpDialogClose(needsUpdate: boolean) {
    setEpDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  async function processPayment(payment: Payment) {
    const url = "/api/payments/" + payment.id + "/process"
    const response = await fetch(url, {method: "POST"})

    if (!response.ok)
      toast({
        title: "Error processing Payment",
        description: response.statusText
      })

    router.refresh()
  }

  return (
    <>
      <div className="w-full relative">
        {payments.map(payment =>
          <PaymentRow key={payment.id} payment={payment} account={accounts.find(acct => acct.id == payment.account_id)}
                                       selectable={exchangeSelection != null}
                                       onProcessPaymentClick={() => processPayment(payment)}
                                       onClick={() => openExchangePaymentDialog(payment)}/>
        )}
      </div>
      <ExchangePaymentDialog open={epDialogOpen} onClose={onEpDialogClose} exchange={exchangeSelection!}
                             payment={paymentSelection!}/>
    </>
  )
}