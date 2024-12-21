import {Separator} from "@/components/ui/separator.tsx";
import CardBalance from "@/components/widgets/CardBalance.tsx";
import {fetchAccounts, fetchAccountBalances, fetchBankAccounts} from "@/requests.ts";
import BankAccountBalance from "@/components/widgets/BankAccountBalance.tsx";

export default async function BalancesWidget() {
  const accounts = await fetchAccounts()
  const accountBalances = await fetchAccountBalances()
  const bankAccounts = await fetchBankAccounts()

  return (
    <>
      {accounts.map(account =>
        <div key={account.id} className="card-balance-container">
          <Separator className="balance-separator mb-4 mt-4"/>
          <CardBalance account={account} accountBalances={accountBalances}/>
        </div>
      )}
      {bankAccounts.map(bankAccount =>
        <div key={bankAccount.id} className="card-balance-container">
          <Separator className="balance-separator mb-4 mt-4"/>
          <BankAccountBalance bankAccount={bankAccount}/>
        </div>
      )}
    </>
  )
}