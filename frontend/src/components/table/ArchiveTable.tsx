import {Account, Transaction} from "@/types.ts";
import ArchiveRow from "@/components/table/ArchiveRow.tsx";

export default function ArchiveTable({
  transactions,
  accounts
}: {
  transactions: Transaction[],
  accounts: Account[],
}) {

  return (
    <div className="w-full relative">
      {transactions.map(tx =>
        <ArchiveRow key={tx["id"]} transaction={tx} account={accounts.find(acct => acct.id == tx.account_id)}/>
      )}
    </div>
  )
}