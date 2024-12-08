import {formatAmount} from "@/components/util.ts";
import {Account, Transaction} from "@/types.ts";
import TableRow from "@/components/table/TableRow.tsx";

export default function ArchiveRow ({
  transaction, account
}: {
  transaction: Transaction,
  account?: Account,
}) {

  return (
    <TableRow style={{borderLeftStyle: transaction.status == 1 ? "dashed" : "solid"}} account={account}
              date={transaction.date} remoteName={transaction.counterparty}
              purpose={transaction.description}>
      <span className="w-16 text-right">{formatAmount(transaction.amount_eur)}</span>
      <span className="w-12 text-right" style={{color: transaction.fees_and_risk_eur! < 0 ? "green" : ""}}>{formatAmount(transaction.fees_and_risk_eur)}</span>
    </TableRow>
  )
}