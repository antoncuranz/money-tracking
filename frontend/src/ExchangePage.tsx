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

const ExchangePage = () => {
  const [exchanges, setExchanges] = useState([]);
  const [payments, setPayments] = useState([]);
  const [balances, setBalances] = useState({});
  const { toast } = useToast();

  useEffect(() => {
    initData()
  }, []);
  async function initData() {
    let response = await fetch("/api/exchanges")
    response = await response.json()
    setExchanges(response as any[])

    response = await fetch("/api/accounts/2/payments") // FIXME
    response = await response.json()
    setPayments(response as any[])

    setBalances(await (await fetch("/api/balance")).json())
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="ml-auto flex items-center gap-2">
              <ExchangeDialog/>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
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
                  <AlertDescription>2 Deposits are not assigned to Exchanges</AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
          <Card className="mt-2">
            <CardHeader className="pb-0">
              <CardTitle>Exchanges</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <ExchangeTable exchanges={exchanges}/>
            </CardContent>
          </Card>
          <Card className="mt-2">
            <CardHeader className="pb-0">
              <CardTitle>Payments</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <PaymentTable payments={payments} showAccount={true}/>
            </CardContent>
          </Card>
        </main>
      </div>
  </>
)
}

export default ExchangePage