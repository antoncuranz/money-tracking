import {formatAmount, titlecase} from "@/components/util.ts";
import {BankAccount} from "@/types.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";
import {getCurrentUser} from "@/requests.ts";

interface Props {
  bankAccount: BankAccount
}

export default async function BankAccountBalance({bankAccount}: Props) {
  const username = await getCurrentUser()
  
  return (
    <div>
      <img className="w-8 mr-2 mt-3 inline-block align-top flex-init" src={bankAccount.icon ?? undefined} alt=""/>
      <div className="inline-block flex-auto">
        <p className="font-medium">
          {bankAccount.user.name != username &&
              <>{titlecase(bankAccount.user.name)}'s </>
          }
          {bankAccount.name}
        </p>
        <p className="text-sm text-muted-foreground">{bankAccount.institution}</p>
        <PrivacyFilter className="mt-2">
          <span className="font-medium">{formatAmount(bankAccount.balance)}</span>
        </PrivacyFilter>
      </div>
    </div>
  )
}