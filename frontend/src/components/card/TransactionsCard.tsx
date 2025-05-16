import TransactionTable from "@/components/table/TransactionTable.tsx";
import {fetchAccounts, fetchTransactions} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import {MissingAmountEurFilter} from "@/components/buttons/MissingAmountEurFilter.tsx";

export default async function TransactionsCard() {
  const accounts = await fetchAccounts()
  const transactions = (await fetchTransactions(false)).filter(tx => tx.status != 3)

  // {/*<Card className={creditSelection == null ? "mb-2 overflow-hidden" : "mb-2 outline overflow-hidden"}>*/}
  return (
    <Card title="Transactions" headerSlot={<MissingAmountEurFilter/>}>
      <TransactionTable transactions={transactions} accounts={accounts}/>
    </Card>
  )
}