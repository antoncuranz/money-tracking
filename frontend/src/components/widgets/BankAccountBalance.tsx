import {formatAmount, titlecase} from "@/components/util.ts";
import {BankAccount} from "@/types.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";
import {getCurrentUser} from "@/requests.ts";
import {HistoryIcon} from "lucide-react";

export default async function BankAccountBalance({
  bankAccount
}: {
  bankAccount: BankAccount
}) {
  const username = await getCurrentUser()
  
  function getLastUpdatedHours() {
    const diffInMs = new Date().getTime() - new Date(bankAccount.last_successful_update!).getTime()
    return Math.floor((diffInMs / (1000 * 60 * 60)))
  }
  
  return (
    <div className="flex">
      <div className="w-8 mr-2 mt-3 inline-block align-top">
        <img src={bankAccount.icon ?? undefined} alt=""/>
      </div>
      <div className="inline-block flex-auto">
        <div>
          <p className="font-medium">
            {bankAccount.user.name != username &&
                <>{titlecase(bankAccount.user.name)}'s </>
            }
            {bankAccount.name}
          </p>
          <p className="text-sm text-muted-foreground">{bankAccount.institution}</p>
        </div>
        <PrivacyFilter className="mt-2 flex">
          <span className="font-medium">{formatAmount(bankAccount.balance)}</span>
          { bankAccount.last_successful_update &&
            <span className="text-muted-foreground text-sm grow text-right">
              <HistoryIcon className="inline size-3 mb-0.5 mr-0.5"/>
              { getLastUpdatedHours() }h
            </span>
          }
        </PrivacyFilter>
      </div>
    </div>
  )
}