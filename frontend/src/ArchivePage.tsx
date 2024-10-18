import './App.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {useEffect, useState} from "react";
import {formatAmount} from "@/components/util.ts";
import ArchiveTable from "@/components/ArchiveTable.tsx";

const ArchivePage = () => {
  const [fees, setFees] = useState<FeeSummary|null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    updateData()
  }, []);
  async function updateData() {
    let response = await fetch("/api/transactions?paid=true")
    const transactions = await response.json() as Transaction[]
    setTransactions(transactions)

    response = await fetch("/api/fee_summary")
    const fees = await response.json() as FeeSummary
    setFees(fees)
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="grid grid-cols-2 gap-2 mb-2">
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>{formatAmount(fees?.fees_and_risk_eur ?? 0)}</CardTitle>
                <CardDescription>
                  TOTAL FX FEES AND CCY RISK
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>TODO</CardTitle>
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