import {Separator} from "@/components/ui/separator.tsx";
import CardBalance from "@/components/widgets/CardBalance.tsx";
import {fetchAccounts, fetchBalances} from "@/requests.ts";

export default async function BalancesWidget() {
  const accounts = await fetchAccounts()
  const balances = await fetchBalances()

  return (
    <>
      {accounts.map(account =>
        <div key={account.id} className="card-balance-container">
          <Separator className="balance-separator mb-4 mt-4"/>
          <CardBalance account={account} balances={balances}/>
        </div>
      )}
    </>
  )
}