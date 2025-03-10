import {fetchAccounts, fetchBankAccounts, fetchPlaidConnections} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import AddCreditCardButton from "@/components/buttons/AddCreditCardButton.tsx";
import React from "react";
import CreditCardTable from "@/components/table/CreditCardTable.tsx";

export default async function CreditCardsCard() {
  const accounts = await fetchAccounts()
  const connections = await fetchPlaidConnections()
  const bank_accounts = await fetchBankAccounts()

  return (
    <Card title="Credit Cards" headerSlot={<AddCreditCardButton connections={connections} bank_accounts={bank_accounts}/>}>
        <CreditCardTable accounts={accounts} bank_accounts={bank_accounts} connections={connections}/>
    </Card>
  )
}