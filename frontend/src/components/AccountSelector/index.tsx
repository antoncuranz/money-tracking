import AccountSelectorClient from "@/components/AccountSelector/client.tsx";
import {fetchAccounts} from "@/requests.ts";

export default async function AccountsSelector() {
  const accounts = await fetchAccounts()

  return <AccountSelectorClient accounts={accounts}/>
}