import './App.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {AlertCircle} from 'lucide-react';
import {useToast} from "@/components/ui/use-toast.ts";
import {useEffect, useState} from "react";
import {Alert, AlertDescription} from "@/components/ui/alert.tsx";
import ExchangeDialog from "@/components/ExchangeDialog.tsx";
import ExchangeTable from "@/components/ExchangeTable.tsx";
import PaymentTable from "@/components/PaymentTable.tsx";
import {formatAmount} from "@/components/util.ts";
import CreditTransactionDialog from "@/components/CreditTransactionDialog.tsx";
import ExchangePaymentDialog from "@/components/ExchangePaymentDialog.tsx";

const ExchangePage = () => {
  const [exchanges, setExchanges] = useState([]);
  const [payments, setPayments] = useState([]);
  const [balances, setBalances] = useState({});

  const [exchangeSelection, setExchangeSelection] = useState<number>(null)
  const [paymentSelection, setPaymentSelection] = useState()
  const [epDialogOpen, setEpDialogOpen] = useState(false)

  const { toast } = useToast();

  useEffect(() => {
    updateData()
  }, []);
  async function updateData() {
    let response = await fetch("/api/exchanges")
    response = await response.json()
    setExchanges(response as any[])

    response = await fetch("/api/accounts/2/payments") // FIXME
    response = await response.json()
    setPayments(response as any[])

    setBalances(await (await fetch("/api/balance")).json())
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

  function openExchangePaymentDialog(payment) {
    if (exchangeSelection != null) {
      setPaymentSelection(payment)
      setEpDialogOpen(true)
    }
  }

  function onDialogClose(needsUpdate) {
    setEpDialogOpen(false)

    if (needsUpdate)
      updateData()
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
            <div className="ml-auto flex items-center gap-2">
              <ExchangeDialog/>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(balances["total"])}</CardTitle>
                <CardDescription>
                  <span className="text-lg">{formatAmount(balances["posted"])} + {formatAmount(balances["pending"])}</span> pending
                  <span className="text-lg"> - {formatAmount(balances["credits"])}</span> credits
                  <span className="text-lg"> - {formatAmount(balances["exchanged"])}</span> exchanged
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
                            onPaymentClick={openExchangePaymentDialog}/>
            </CardContent>
          </Card>
        </main>
      </div>
      <ExchangePaymentDialog open={epDialogOpen} onClose={onDialogClose} exchange={exchangeSelection} payment={paymentSelection}/>
  </>
)
}

export default ExchangePage