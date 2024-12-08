import {Account, Balances, Credit, Exchange, FeeSummary, Payment, Transaction} from "@/types.ts";

async function fetchData(url: string) {
  const response = await fetch(process.env.BACKEND_URL + url, {cache: "no-cache"})
  if (!response.ok) {
    throw new Error("Failed to fetch data");
  }
  return await response.json()
}

export async function fetchAccounts() {
  return await fetchData("/api/accounts") as Account[]
}

export async function fetchTransactions(paid: boolean = true) {
  const suffix = "?paid=" + paid
  return await fetchData("/api/transactions" + suffix) as Transaction[]
}

export async function fetchCredits(usable: boolean = true) {
  const suffix = "?usable=" + usable
  return await fetchData("/api/credits" + suffix) as Credit[]
}

export async function fetchExchanges(usable: boolean = true) {
  const suffix = "?usable=" + usable
  return await fetchData("/api/exchanges" + suffix) as Exchange[]
}

export async function fetchPayments() {
  return await fetchData("/api/payments") as Payment[]
}

export async function fetchBalances() {
  return await fetchData("/api/balance") as Balances
}

export async function fetchFees() {
  return await fetchData("/api/fee_summary") as FeeSummary
}
