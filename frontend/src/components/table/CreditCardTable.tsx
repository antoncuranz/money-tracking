"use client"

import {Account, BankAccount, PlaidConnection} from "@/types.ts";
import CreditCardRow from "@/components/table/CreditCardRow.tsx";
import {useState} from "react";
import {useRouter} from "next/navigation";
import CreditCardDialog from "@/components/dialog/CreditCardDialog.tsx";

export default function CreditCardTable({
  accounts,
  bank_accounts,
  connections
}: {
  accounts: Account[],
  bank_accounts: BankAccount[],
  connections: PlaidConnection[]
}) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogAccount, setDialogAccount] = useState<Account|null>(null)
  const router = useRouter()
  
  async function editAccount(account: Account) {
    setDialogAccount(account)
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
        {accounts.map(account =>
          <CreditCardRow key={account.id} account={account} editAccount={() => editAccount(account)}/>
        )}
      </div>
      <CreditCardDialog open={dialogOpen} onClose={onDialogClose} connections={connections} bank_accounts={bank_accounts} account={dialogAccount}/>
    </>
  )
}
