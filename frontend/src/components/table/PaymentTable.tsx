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

  async function mutatePayment(url: string, method: "POST" | "DELETE", title: string, description?: string) {
    const response = await fetch(url, {method})

    if (!response.ok)
      toast({
        title,
        description: description || await response.text() || response.statusText
      })

    if (response.ok)
      router.refresh()
  }

  async function processPayment(payment: Payment) {
    await mutatePayment(
      "/api/payments/" + payment.id + "/process",
      "POST",
      "Payment processing failed",
      "Changes were not saved and were reverted."
    )
  }

  async function unprocessPayment(payment: Payment) {
    await mutatePayment("/api/payments/" + payment.id + "/unprocess", "POST", "Error unprocessing payment")
  }

  async function deletePayment(payment: Payment) {
    await mutatePayment("/api/payments/" + payment.id, "DELETE", "Error deleting payment")
  }

  return (
    <>
      <div className="w-full relative">
        {payments.map(payment =>
          <PaymentRow key={payment.id} payment={payment} account={accounts.find(acct => acct.id == payment.account_id)}
                                        selectable={exchangeSelection != null}
                                        onProcessPaymentClick={() => processPayment(payment)}
                                        onUnprocessPaymentClick={() => unprocessPayment(payment)}
                                        onDeletePaymentClick={() => deletePayment(payment)}
                                        onClick={() => openExchangePaymentDialog(payment)}/>
        )}
      </div>
      <ExchangePaymentDialog open={epDialogOpen} onClose={onEpDialogClose} exchange={exchangeSelection!}
                             payment={paymentSelection!}/>
    </>
  )
}
