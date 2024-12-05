import {ClientOnly} from "@/app/exchanges/client.tsx";

export function generateStaticParams() {
  return [{ slug: [''] }]
}

export default async function Page() {
  const exchangesResponse = await fetch(process.env.BACKEND_URL + "/api/exchanges?usable=true")
  const exchanges = await exchangesResponse.json() as Exchange[]

  const paymentsResponse = await fetch(process.env.BACKEND_URL + "/api/payments")
  const payments = await paymentsResponse.json() as Payment[]

  const balancesResponse = await fetch(process.env.BACKEND_URL + "/api/balance")
  const balances = await balancesResponse.json() as Balances

  return <ClientOnly exchanges={exchanges} payments={payments} balances={balances}/>
}