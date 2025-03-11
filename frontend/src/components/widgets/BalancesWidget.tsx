import {Separator} from "@/components/ui/separator.tsx";
import CardBalance from "@/components/widgets/CardBalance.tsx";
import {fetchAccounts, fetchAccountBalances, fetchBankAccounts, getCurrentUser} from "@/requests.ts";
import BankAccountBalance from "@/components/widgets/BankAccountBalance.tsx";
import {User} from "@/types.ts";

export default async function BalancesWidget({
  showMyAccounts = true
}: {
  showMyAccounts?: boolean
}) {
  const username = await getCurrentUser()
  const accounts = await fetchAccounts()
  const accountBalances = await fetchAccountBalances()
  const bankAccounts = await fetchBankAccounts()
  
  function myAccounts(account: {user: User}) {
    return (account.user.name == username) == showMyAccounts
  }

  return (
    <>
      {accounts.filter(myAccounts).map(account =>
        <div key={account.id} className="card-balance-container">
          <Separator className="balance-separator mb-4 mt-4"/>
          <CardBalance account={account} accountBalances={accountBalances}/>
        </div>
      )}
      {bankAccounts.filter(myAccounts).map(bankAccount =>
        <div key={bankAccount.id} className="card-balance-container">
          <Separator className="balance-separator mb-4 mt-4"/>
          <BankAccountBalance bankAccount={bankAccount}/>
        </div>
      )}
    </>
  )
}