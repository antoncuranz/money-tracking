import {Account} from "@/types.ts";
import AccountSelectorClient from "@/components/AccountSelector/client.tsx";

export default async function AccountsSelector() {
  const accountResponse = await fetch(process.env.BACKEND_URL + "/api/accounts", {cache: "no-cache"})
  const accounts = await accountResponse.json() as Account[]

  return <AccountSelectorClient accounts={accounts}/>
}