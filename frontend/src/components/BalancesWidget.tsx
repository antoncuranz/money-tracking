import {Account, Balances} from "@/types.ts";
import {Separator} from "@/components/ui/separator.tsx";
import CardBalance from "@/components/CardBalance.tsx";

export default async function BalancesWidget({
  accounts
}: {
  accounts: Account[]
}) {

  const balancesResponse = await fetch(process.env.BACKEND_URL + "/api/balance", {cache: "no-cache"})
  const balances = await balancesResponse.json() as Balances

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