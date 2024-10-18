import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {formatAmount} from "@/components/util.ts";

interface Props {
  transaction: Transaction,
}

const ArchiveRow = ({transaction}: Props) => {

  return (
    <TableRow>
      <TableCell>{transaction.date.substring(0, 16)}</TableCell>
      <TableCell>{transaction.account_id}</TableCell>
      <TableCell>{transaction.counterparty}</TableCell>
      <TableCell>{transaction.description}</TableCell>
      <TableCell className="text-right">
        {formatAmount(transaction.amount_eur)}
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(transaction.fees_and_risk_eur)}
      </TableCell>
    </TableRow>
  )
}

export default ArchiveRow