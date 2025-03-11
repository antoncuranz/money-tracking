import {
  Account,
  AccountBalances,
  Balances,
  BankAccount,
  Credit,
  Exchange,
  FeeSummary,
  Payment, PlaidConnection,
  Transaction
} from "@/types.ts";
import {headers} from "next/headers";
import React from "react";

class UnauthorizedError extends Error {}

export async function hideIfUnauthorized(func: () => Promise<React.ReactElement>) {
  try {
    return await func()
  } catch (e: unknown) {
    if (e instanceof UnauthorizedError)
      return ""
    else
      throw e
  }
}

const usernameHeader = "X-Auth-Request-Preferred-Username"

async function fetchData(url: string) {
  const response = await fetch(process.env.BACKEND_URL + url, {
    headers: {[usernameHeader]: await getCurrentUser()},
    cache: "no-cache"
  })
  if (response.status == 401) {
    throw new UnauthorizedError()
  } else if (!response.ok) {
    throw new Error("Failed to fetch data");
  }
  return await response.json()
}

export async function getCurrentUser(): Promise<string> {
  const usernameFromHeader = (await headers()).get(usernameHeader)
  if (usernameFromHeader)
    return usernameFromHeader
  
  // get user from backend call (only for development)
  const response = await fetch(process.env.BACKEND_URL + "/api/username", {cache: "no-cache"})
  
  if (response.ok)
    return await response.json()
  else
    throw new Error("Failed to fetch data");
}

export async function isSuperUser(): Promise<boolean> {
  return await fetchData("/api/user/super") as boolean
}

export async function fetchAccounts() {
  return await fetchData("/api/accounts") as Account[]
}

export async function fetchBankAccounts() {
  return await fetchData("/api/bank_accounts") as BankAccount[]
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

export async function fetchAccountBalances() {
  return await fetchData("/api/balance/accounts") as AccountBalances
}

export async function fetchFees() {
  return await fetchData("/api/balance/fees") as FeeSummary
}

export async function fetchPlaidConnections() {
  return await fetchData("/api/import/plaid/connections") as PlaidConnection[]
}
