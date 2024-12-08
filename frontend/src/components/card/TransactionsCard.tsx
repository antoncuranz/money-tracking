import {Account, Transaction} from "@/types.ts";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import TransactionTable from "@/components/table/TransactionTable.tsx";

export default async function TransactionsCard() {
  const accountResponse = await fetch(process.env.BACKEND_URL + "/api/accounts", {cache: "no-cache"})
  const accounts = await accountResponse.json() as Account[]

  const txResponse = await fetch(process.env.BACKEND_URL + "/api/transactions?paid=false", {cache: "no-cache"})
  let transactions = await txResponse.json() as Transaction[]
  transactions = transactions.filter(tx => tx.status != 3)

  // {/*<Card className={creditSelection == null ? "mb-2 overflow-hidden" : "mb-2 outline overflow-hidden"}>*/}
  return (
    <Card className="mb-2 overflow-hidden">
      <CardHeader className="pb-0">
        <CardTitle>Transactions</CardTitle>
        <CardDescription/>
      </CardHeader>
      <CardContent className="p-0">
        <Separator className="balance-separator mt-4"/>
        <TransactionTable transactions={transactions} accounts={accounts}/>
      </CardContent>
    </Card>
  )
}