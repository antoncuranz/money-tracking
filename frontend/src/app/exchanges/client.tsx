'use client'

import {Button} from "@/components/ui/button.tsx";
import {Coins} from "lucide-react";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import ExchangeTable from "@/components/ExchangeTable.tsx";
import PaymentTable from "@/components/PaymentTable.tsx";
import ExchangeDialog from "@/components/ExchangeDialog.tsx";
import ExchangePaymentDialog from "@/components/ExchangePaymentDialog.tsx";
import {useState} from "react";
import {useToast} from "@/components/ui/use-toast.ts";
import {useRouter} from "next/navigation";
import {Exchange, Payment, Balances} from "@/types.ts";

export function ClientOnly({
  exchanges,
  payments,
  balances
}: {
  exchanges: Exchange[],
  payments: Payment[],
  balances: Balances,
}) {
  const [exchangeSelection, setExchangeSelection] = useState<number|null>(null)
  const [paymentSelection, setPaymentSelection] = useState<Payment>()
  const [epDialogOpen, setEpDialogOpen] = useState(false)
  const [exchangeDialogOpen, setExchangeDialogOpen] = useState(false)

  const { toast } = useToast();
  const router = useRouter();

  async function deleteExchange(exId: number) {
    const url = "/api/exchanges/" + exId
    const response = await fetch(url, {method: "DELETE"})

    if (response.ok)
      router.refresh()
    else toast({
      title: "Error deleting Exchange",
      description: response.statusText
    })
  }

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

  function onExchangeDialogClose(needsUpdate: boolean) {
    setExchangeDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  async function processPayment(payment: Payment) {
    const url = "/api/accounts/" + payment.account_id + "/payments/" + payment.id
    const response = await fetch(url, {method: "POST"})

    if (!response.ok)
      toast({
        title: "Error processing Payment",
        description: response.statusText
      })

    router.refresh()
  }

  return (<>
          <div className="flex items-center h-10">
            <div className="ml-auto flex items-center gap-2">
              <Button size="sm" className="h-8 gap-1" onClick={() => setExchangeDialogOpen(true)}>
                <Coins className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Add Exchange
                </span>
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(balances?.total ?? 0)}</CardTitle>
                <CardDescription>
                  <span className="text-lg">{formatAmount(balances?.posted ?? 0)} + {formatAmount(balances?.pending ?? 0)}</span> pending
                  <span className="text-lg"> - {formatAmount(balances?.credits ?? 0)}</span> credits
                  <span className="text-lg"> - {formatAmount(balances?.exchanged ?? 0)}</span> exchanged
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(balances?.virtual_account ?? 0)}</CardTitle>
                <CardDescription>
                  <span className="text-lg">virtual account balance</span>
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
          </div>
          <Card className="mb-2">
            <CardHeader className="pb-0">
              <CardTitle>Exchanges</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <ExchangeTable exchanges={exchanges} selectedExchange={exchangeSelection} selectExchange={setExchangeSelection}
                             unselectExchange={() => setExchangeSelection(null)} deleteExchange={deleteExchange}/>
            </CardContent>
          </Card>
          <Card className={exchangeSelection == null ? "mb-2" : "mb-2 outline"}>
            <CardHeader className="pb-0">
              <CardTitle>Payments</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <PaymentTable payments={payments} showAccount={true} selectable={exchangeSelection != null}
                            onProcessPaymentClick={processPayment}
                            onPaymentClick={openExchangePaymentDialog}/>
            </CardContent>
          </Card>
      <ExchangeDialog open={exchangeDialogOpen} onClose={onExchangeDialogClose}/>
      <ExchangePaymentDialog open={epDialogOpen} onClose={onEpDialogClose} exchange={exchangeSelection!} payment={paymentSelection!}/>
    </>
  )
}