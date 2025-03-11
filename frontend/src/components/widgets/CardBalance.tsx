import {formatAmount, titlecase} from "@/components/util.ts";
import {Progress} from "@/components/ui/progress.tsx";
import {Account, AccountBalances} from "@/types.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";
import {getCurrentUser} from "@/requests.ts";

export default async function CardBalance({
  account, accountBalances
}: {
  account: Account,
  accountBalances: AccountBalances
}) {
  const username = await getCurrentUser()
  
  function getTotalSpent(account: Account) {
    return accountBalances[account.id].total_spent
  }

  function getTotalCredits(account: Account) {
    return accountBalances[account.id].total_credits
  }

  return (
    <div>
      <img className="w-8 mr-2 mt-3 inline-block align-top flex-init" src={account.icon ?? ""} alt=""/>
      <div className="inline-block flex-auto">
        <p className="font-medium">
          {account.user.name != username &&
            <>{titlecase(account.user.name)}'s </>
          }
          {account.name}
        </p>
        <p className="text-sm text-muted-foreground">{account.institution}</p>
        <PrivacyFilter className="mt-2">
          <span className="font-medium">{formatAmount(accountBalances[account.id].posted)}</span>
          <span className="text-sm text-muted-foreground"> + {formatAmount(accountBalances[account.id].pending)} pending</span>
        </PrivacyFilter>
        {account.target_spend &&
            <PrivacyFilter>
              <Progress value={(getTotalSpent(account) - getTotalCredits(account)) / account.target_spend}
                        secondaryValue={getTotalSpent(account) / account.target_spend} className="mt-2"/>
              <span className="text-sm font-medium">{formatAmount(getTotalSpent(account))}</span>
              {getTotalCredits(account) > 0 &&
                  <span className="text-sm text-muted-foreground"> - {formatAmount(getTotalCredits(account))}</span>
              }
              <span className="text-sm font-medium float-right"> / {account.target_spend}</span>
            </PrivacyFilter>
        }
      </div>
    </div>
  )
}
