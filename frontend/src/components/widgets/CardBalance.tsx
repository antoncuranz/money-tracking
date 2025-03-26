import {formatAmount, titlecase} from "@/components/util.ts";
import {Progress} from "@/components/ui/progress.tsx";
import {Account, AccountBalance, AccountBalances} from "@/types.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";
import {getCurrentUser} from "@/requests.ts";
import {HistoryIcon} from "lucide-react";

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
  
  function getLastUpdatedHours(accountBalance: AccountBalance) {
    const diffInMs = new Date().getTime() - new Date(accountBalance.last_successful_update!).getTime()
    return Math.floor((diffInMs / (1000 * 60 * 60)))
  }

  return (
    <div className="flex">
      <div className="w-8 mr-2 mt-3 inline-block align-top">
        <img src={account.icon ?? undefined} alt=""/>
      </div>
      <div className="inline-block flex-auto">
        <div>
          <p className="font-medium">
            {account.user.name != username &&
              <>{titlecase(account.user.name)}'s </>
            }
            {account.name}
          </p>
          <p className="text-sm text-muted-foreground">{account.institution}</p>
        </div>
        <PrivacyFilter className="mt-2 flex items-end">
          <span className="font-medium">{formatAmount(accountBalances[account.id].posted)}</span>
          { accountBalances[account.id].pending != 0 &&
            <span className="text-sm text-muted-foreground ml-1">+ {formatAmount(accountBalances[account.id].pending)} pend.</span>
          }
          { accountBalances[account.id].last_successful_update &&
            <span className="text-muted-foreground text-sm grow text-right">
              <HistoryIcon className="inline size-3 mb-0.5 mr-0.5"/>
              { getLastUpdatedHours(accountBalances[account.id]) }h
            </span>
          }
        </PrivacyFilter>
        {account.target_spend &&
          <PrivacyFilter>
            <Progress value={(getTotalSpent(account) - getTotalCredits(account)) / account.target_spend}
                      secondaryValue={getTotalSpent(account) / account.target_spend} className="mt-2"/>
            <div className="flex">
              <span className="text-sm font-medium">{formatAmount(getTotalSpent(account))}</span>
              {getTotalCredits(account) > 0 &&
                  <span className="text-sm text-muted-foreground ml-1">- {formatAmount(getTotalCredits(account))}</span>
              }
              <span className="text-sm font-medium grow text-right"> / {account.target_spend}</span>
            </div>
          </PrivacyFilter>
        }
      </div>
    </div>
  )
}
