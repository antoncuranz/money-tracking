import './App.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {useEffect, useState} from "react";
import {formatAmount} from "@/components/util.ts";
import ArchiveTable from "@/components/ArchiveTable.tsx";

const ArchivePage = () => {
  const [fees, setFees] = useState({});
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    updateData()
  }, []);
  async function updateData() {
    let response = await fetch("/api/transactions?paid=true")
    response = await response.json()
    setTransactions(response as any[])

    setFees(await (await fetch("/api/fee_summary")).json())
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="grid grid-cols-3 gap-2 mb-2">
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(fees["fx_fees"])}</CardTitle>
                <CardDescription>
                  TOTAL FX FEES
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(fees["ccy_risk"])}</CardTitle>
                <CardDescription>
                  TOTAL CCY RISK
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>TODO</CardTitle>
                <CardDescription>
                  TOTAL CASHBACK
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
          </div>
          <Card className="mb-2">
            <CardHeader className="pb-0">
              <CardTitle>Transactions</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <ArchiveTable transactions={transactions}/>
            </CardContent>
          </Card>
        </main>
      </div>
  </>
)
}

export default ArchivePage