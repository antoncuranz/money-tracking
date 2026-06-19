import StatementMatchPageClient from "@/components/statement-match/StatementMatchPageClient.tsx";
import {fetchAccounts, getCurrentUser} from "@/requests.ts";

export const dynamic = 'force-dynamic'

export default async function Page() {
  const username = await getCurrentUser()
  const accounts = (await fetchAccounts()).filter(account => account.user.name === username)

  return <StatementMatchPageClient accounts={accounts}/>
}
