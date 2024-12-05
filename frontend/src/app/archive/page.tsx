import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import ArchiveTable from "@/components/ArchiveTable.tsx";
import {Transaction, FeeSummary} from "@/types.ts";

export function generateStaticParams() {
  return [{ slug: [''] }]
}

export default async function Page() {
  const transactionsResponse = await fetch(process.env.BACKEND_URL + "/api/transactions?paid=true", {cache: "no-cache"})
  const transactions = await transactionsResponse.json() as Transaction[]

  const feesResponse = await fetch(process.env.BACKEND_URL + "/api/fee_summary", {cache: "no-cache"})
  const fees = await feesResponse.json() as FeeSummary

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