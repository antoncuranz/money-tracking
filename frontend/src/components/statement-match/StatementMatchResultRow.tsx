import EditableTransactionRow from "@/components/table/EditableTransactionRow.tsx";
import {formatAmount} from "@/components/util.ts";
import {Button} from "@/components/ui/button.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {Progress} from "@/components/ui/progress.tsx";
import {Account, StatementMatchResult} from "@/types.ts";
import {Info} from "lucide-react";

interface Props {
  row: StatementMatchResult;
  account?: Account;
  amount: number | null;
  onAmountChange: (amount: number | null) => void;
}

const StatementMatchResultRow = ({row, account, amount, onAmountChange}: Props) => {
  return (
    <EditableTransactionRow
      account={account}
      date={row.date}
      remoteName={row.counterparty}
      purpose={row.description}
      amount={amount}
      placeholderAmount={row.guessed_amount_eur}
      onAmountChange={onAmountChange}
      beforeAmountInput={
        <div className="flex items-center gap-3">
          <div className="w-24 space-y-1">
            <Progress value={Math.round(row.confidence * 100)}/>
            <div className="text-right text-xs text-muted-foreground">{Math.round(row.confidence * 100)}%</div>
          </div>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
                <Info className="h-4 w-4"/>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className="space-y-3">
              <div>
                <div className="text-sm font-medium">Statement excerpt</div>
                <div className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">{row.statement_excerpt ?? "—"}</div>
              </div>
              <div>
                <div className="text-sm font-medium">Reason</div>
                <div className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">{row.reason}</div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      }
      afterAmountInput={<span className="price text-sm">{formatAmount(row.amount_usd)}</span>}
    />
  )
}

export default StatementMatchResultRow
