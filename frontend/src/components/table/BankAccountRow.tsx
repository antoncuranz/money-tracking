import {Pencil} from "lucide-react";
import {Button} from "@/components/ui/button.tsx";
import {BankAccount} from "@/types.ts";
import React from "react";

export default function BankAccountRow({
  bankAccount, editBankAccount
}: {
  bankAccount: BankAccount,
  editBankAccount: () => void
}) {

  return (
    <div className="containers tx-row-border">
      <div className="left-nowrap">
        <img className="w-8 ml-1" src={bankAccount.icon} alt=""/>
        <div className="font-medium">{bankAccount.institution}</div>
        <div>{bankAccount.name}</div>
      </div>
      <div className="right">
        <Button variant="outline" size="icon" onClick={editBankAccount}>
          <Pencil className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}