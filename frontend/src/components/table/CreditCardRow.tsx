import {Pencil} from "lucide-react";
import {Button} from "@/components/ui/button.tsx";
import {Account} from "@/types.ts";
import React from "react";
import {titlecase} from "@/components/util.ts";
import {useUser} from "@/components/provider/UserProvider.tsx";

export default function CreditCardRow({
  account, editAccount
}: {
  account: Account
  editAccount: () => void
}) {
  const {username} = useUser()
  
  return (
    <div className="containers tx-row-border border-l-4" style={{borderLeftColor: account.color ?? "transparent"}}>
      <div className="left-nowrap">
        <img className="w-8" src={account.icon ?? undefined} alt=""/>
        <div className="font-medium">{account.institution}</div>
        <div>
          {account.user.name != username &&
            <>{titlecase(account.user.name)}'s </>
          }
          {account.name}
        </div>
      </div>
      <div className="right">
        <Button variant="outline" size="icon" onClick={editAccount}>
          <Pencil className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}