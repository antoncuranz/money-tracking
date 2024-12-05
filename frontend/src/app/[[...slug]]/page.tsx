import {ClientOnly} from "@/app/[[...slug]]/client.tsx";
import {Account, Transaction, Credit, Balances} from "@/types.ts";

export function generateStaticParams() {
  return [{ slug: [''] }]
}

export default async function Page() {
  const accountResponse = await fetch(process.env.BACKEND_URL + "/api/accounts", {cache: "no-cache"})
  const accounts = await accountResponse.json() as Account[]

  const txResponse = await fetch(process.env.BACKEND_URL + "/api/transactions?paid=false", {cache: "no-cache"})
  let transactions = await txResponse.json() as Transaction[]
  transactions = transactions.filter(tx => tx.status != 3)

  const creditResponse = await fetch(process.env.BACKEND_URL + "/api/credits?usable=true", {cache: "no-cache"})
  const credits = await creditResponse.json() as Credit[]

  const balancesResponse = await fetch(process.env.BACKEND_URL + "/api/balance", {cache: "no-cache"})
  const balances = await balancesResponse.json() as Balances

  return <ClientOnly accounts={accounts} transactions={transactions} credits={credits} balances={balances}/>
}