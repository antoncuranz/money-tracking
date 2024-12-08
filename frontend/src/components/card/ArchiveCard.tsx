import {fetchAccounts, fetchTransactions} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import ArchiveTable from "@/components/table/ArchiveTable.tsx";

export default async function ArchiveCard() {
  const accounts = await fetchAccounts()
  const transactions = await fetchTransactions()

  return (
    <Card title="Paid Transactions">
        <ArchiveTable transactions={transactions} accounts={accounts}/>
    </Card>
  )
}