import {TableCell, TableRow} from "@/components/ui/table.tsx";
import {Check, Clock} from "lucide-react";
import AmountInput from "@/components/AmountInput.tsx";
import {formatAmount} from "@/components/util.ts";
import {MouseEventHandler} from "react";

interface Props {
  transaction: any,
}

const ArchiveRow = ({transaction}: Props) => {

  return (
    <TableRow>
      <TableCell>{transaction["date"].substring(0, 16)}</TableCell>
      <TableCell>{transaction["account_id"]}</TableCell>
      <TableCell>{transaction["counterparty"]}</TableCell>
      <TableCell>{transaction["description"]}</TableCell>
      <TableCell className="text-right">
        {formatAmount(transaction["amount_usd"])}
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(transaction["fx_fees"])}
      </TableCell>
      <TableCell className="text-right">
        {formatAmount(transaction["ccy_risk"])}
      </TableCell>
    </TableRow>
  )
}

export default ArchiveRow