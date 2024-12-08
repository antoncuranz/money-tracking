import {fetchAccounts, fetchPayments} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import PaymentTable from "@/components/table/PaymentTable.tsx";

export default async function PaymentsCard() {
  const accounts = await fetchAccounts()
  const payments = await fetchPayments()

  return (
    <Card title="Payments">
        <PaymentTable payments={payments} accounts={accounts}/>
    </Card>
  )
}