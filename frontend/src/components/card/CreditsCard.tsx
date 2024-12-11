import CreditTable from "@/components/table/CreditTable.tsx";
import {fetchAccounts, fetchCredits} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";

export default async function CreditsCard() {
  const accounts = await fetchAccounts()
  const credits = await fetchCredits()

  return (
    <Card title="Credits">
        <CreditTable credits={credits} accounts={accounts}/>
    </Card>
  )
}