import {formatAmount} from "@/components/util.ts";
import {Progress} from "@/components/ui/progress.tsx";

interface Props {
  account: Account,
  balances: Balances,
}

const CardBalance = ({account, balances}: Props) => {
  
  function getTotalSpent(account: Account) {
    return balances.accounts[account.id].total_spent
  }

  function getTotalCredits(account: Account) {
    return balances.accounts[account.id].total_credits
  }

  return (
    <div className="flex">
      <img className="h-5 mr-2 mt-3 inline-block align-top flex-init" src={account.icon} alt=""/>
      <div className="inline-block flex-auto">
        <p className="font-medium">{account.name}</p>
        <p className="text-sm text-muted-foreground">{account.institution}</p>
        <div className="mt-2">
          <span className="font-medium">{formatAmount(balances.accounts[account.id].posted)}</span>
          <span className="text-sm text-muted-foreground"> + {formatAmount(balances.accounts[account.id].pending)} pending</span>
        </div>
        {account.target_spend &&
            <div>
              <Progress value={(getTotalSpent(account) - getTotalCredits(account)) / account.target_spend}
                        secondaryValue={getTotalSpent(account) / account.target_spend} className="mt-2"/>
              <span className="text-sm font-medium">{formatAmount(getTotalSpent(account))}</span>
              {getTotalCredits(account) > 0 &&
                  <span className="text-sm text-muted-foreground"> - {formatAmount(getTotalCredits(account))}</span>
              }
              <span className="text-sm font-medium float-right"> / {account.target_spend}</span>
            </div>
        }
      </div>
    </div>
  )
}

export default CardBalance