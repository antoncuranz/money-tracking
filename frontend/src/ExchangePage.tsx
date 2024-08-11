import './App.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {AlertCircle, Coins} from 'lucide-react';
import {useToast} from "@/components/ui/use-toast.ts";
import {useEffect, useState} from "react";
import {Alert, AlertDescription} from "@/components/ui/alert.tsx";
import ExchangeDialog from "@/components/ExchangeDialog.tsx";
import ExchangeTable from "@/components/ExchangeTable.tsx";
import PaymentTable from "@/components/PaymentTable.tsx";
import {formatAmount} from "@/components/util.ts";
import ExchangePaymentDialog from "@/components/ExchangePaymentDialog.tsx";
import {Button} from "@/components/ui/button.tsx";

const ExchangePage = () => {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [balances, setBalances] = useState<Balances|null>();

  const [exchangeSelection, setExchangeSelection] = useState<number|null>(null)
  const [paymentSelection, setPaymentSelection] = useState<Payment>()
  const [epDialogOpen, setEpDialogOpen] = useState(false)
  const [exchangeDialogOpen, setExchangeDialogOpen] = useState(false)

  const { toast } = useToast();

  useEffect(() => {
    updateData()
  }, []);
  async function updateData() {
    let response = await fetch("/api/exchanges?usable=true")
    const exchanges = await response.json() as Exchange[]
    setExchanges(exchanges)

    response = await fetch("/api/payments")
    const payments = await response.json() as Payment[]
    setPayments(payments)

    response = await fetch("/api/balance")
    const balances = await response.json() as Balances
    setBalances(balances)
  }

  async function deleteExchange(exId: number) {
    const url = "/api/exchanges/" + exId
    const response = await fetch(url, {method: "DELETE"})
    if (response.ok)
      updateData()
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
      updateData()
  }

  function onExchangeDialogClose(needsUpdate: boolean) {
    setExchangeDialogOpen(false)

    if (needsUpdate)
      updateData()
  }

  async function processPayment(payment: Payment) {
    const url = "/api/accounts/" + payment.account_id + "/payments/" + payment.id
    const response = await fetch(url, {method: "POST"})

    if (!response.ok)
      toast({
        title: "Error processing Payment",
        description: response.statusText
      })

    updateData()
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
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
              </CardHeader>
              <CardContent>
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>TODO</AlertDescription>
                </Alert>
              </CardContent>
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
        </main>
      </div>
      <ExchangeDialog open={exchangeDialogOpen} onClose={onExchangeDialogClose}/>
      <ExchangePaymentDialog open={epDialogOpen} onClose={onEpDialogClose} exchange={exchangeSelection!} payment={paymentSelection!}/>
  </>
)
}

export default ExchangePage