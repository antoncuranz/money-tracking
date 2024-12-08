import {ClientOnly} from "@/app/exchanges/client.tsx";
import {Exchange, Payment, Balances} from "@/types.ts";

export default async function Page() {
  const exchangesResponse = await fetch(process.env.BACKEND_URL + "/api/exchanges?usable=true", {cache: "no-cache"})
  const exchanges = await exchangesResponse.json() as Exchange[]

  const paymentsResponse = await fetch(process.env.BACKEND_URL + "/api/payments", {cache: "no-cache"})
  const payments = await paymentsResponse.json() as Payment[]

  const balancesResponse = await fetch(process.env.BACKEND_URL + "/api/balance", {cache: "no-cache"})
  const balances = await balancesResponse.json() as Balances

  return <ClientOnly exchanges={exchanges} payments={payments} balances={balances}/>
}