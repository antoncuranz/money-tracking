"use client"

import {BankAccount, PlaidConnection} from "@/types.ts";
import BankAccountRow from "@/components/table/BankAccountRow.tsx";
import BankAccountDialog from "@/components/dialog/BankAccountDialog.tsx";
import {useState} from "react";
import {useRouter} from "next/navigation";

export default function BankAccountTable({
  bankAccounts, connections
}: {
  bankAccounts: BankAccount[],
  connections: PlaidConnection[]
}) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogBankAccount, setDialogBankAccount] = useState<BankAccount|null>(null)
  const router = useRouter()
  
  async function editBankAccount(bank_account: BankAccount) {
    setDialogBankAccount(bank_account)
    setDialogOpen(true)
  }
  
  function onDialogClose(needsUpdate: boolean) {
    setDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  return (
    <>
      <div className="w-full relative">
        {bankAccounts.map(bankAccount =>
          <BankAccountRow key={bankAccount.id} bankAccount={bankAccount} editBankAccount={() => editBankAccount(bankAccount)}/>
        )}
      </div>
      <BankAccountDialog open={dialogOpen} onClose={onDialogClose} connections={connections} bank_account={dialogBankAccount}/>
    </>
  )
}
