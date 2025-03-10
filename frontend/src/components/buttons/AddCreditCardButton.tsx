"use client"

import {Button} from "@/components/ui/button.tsx";
import {CreditCard} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import CreditCardDialog from "@/components/dialog/CreditCardDialog.tsx";
import {BankAccount, PlaidConnection} from "@/types.ts";

export default function AddCreditCardButton({
  connections, bank_accounts
}: {
  connections: PlaidConnection[],
  bank_accounts: BankAccount[]
}) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const router = useRouter()

  function onDialogClose(needsUpdate: boolean) {
    setDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  return (
    <>
      <Button size="sm" className="h-8 gap-1 mt-0 self-end" onClick={() => setDialogOpen(true)}>
        <CreditCard className="h-3.5 w-3.5"/>
        <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
          Add Credit Card
        </span>
      </Button>
      <CreditCardDialog connections={connections} bank_accounts={bank_accounts} open={dialogOpen} onClose={onDialogClose}/>
    </>
  )
}