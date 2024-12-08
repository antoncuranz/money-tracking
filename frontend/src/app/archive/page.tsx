import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import ArchiveTable from "@/components/table/ArchiveTable.tsx";
import {fetchFees, fetchTransactions} from "@/requests.ts";

export default async function Page() {
  const transactions = await fetchTransactions()
  const fees = await fetchFees()

  return (<>
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
  </>
  )
}