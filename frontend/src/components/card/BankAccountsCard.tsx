import {fetchBankAccounts, fetchPlaidConnections} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import AddBankAccountButton from "@/components/buttons/AddBankAccountButton.tsx";
import React from "react";
import BankAccountTable from "@/components/table/BankAccountTable.tsx";

export default async function BankAccountsCard() {
  const bankAccounts = await fetchBankAccounts()
  const connections = await fetchPlaidConnections()

  return (
    <Card title="Bank Accounts" headerSlot={<AddBankAccountButton connections={connections}/>}>
        <BankAccountTable bankAccounts={bankAccounts} connections={connections}/>
    </Card>
  )
}