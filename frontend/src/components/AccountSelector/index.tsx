import AccountSelectorClient from "@/components/AccountSelector/client.tsx";
import {fetchAccounts, getCurrentUser} from "@/requests.ts";

export default async function AccountsSelector() {
  const username = await getCurrentUser()
  const accounts = (await fetchAccounts()).filter(account => account.user.name == username)

  return <AccountSelectorClient accounts={accounts}/>
}