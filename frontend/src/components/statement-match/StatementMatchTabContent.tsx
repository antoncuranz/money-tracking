import StatementMatchResultRow from "@/components/statement-match/StatementMatchResultRow.tsx";
import {Account, StatementMatchTab} from "@/types.ts";
import {LoaderCircle} from "lucide-react";

interface Props {
  tab: StatementMatchTab;
  accountsById: Map<number, Account>;
  onAmountChange: (transactionId: number, amount: number | null) => void;
}

const StatementMatchTabContent = ({tab, accountsById, onAmountChange}: Props) => {
  if (tab.status === "loading") {
    return (
      <div className="flex min-h-[20rem] items-center justify-center gap-3 text-muted-foreground">
        <LoaderCircle className="h-5 w-5 animate-spin"/>
        Matching statement...
      </div>
    )
  }

  if (tab.status === "error") {
    return (
      <div className="flex min-h-[20rem] items-center justify-center p-6 text-center text-sm text-muted-foreground">
        {tab.error ?? "Unable to match this statement."}
      </div>
    )
  }

  if (tab.rows.length === 0) {
    return (
      <div className="flex min-h-[20rem] items-center justify-center p-6 text-center text-sm text-muted-foreground">
        No matched transactions were found for this statement.
      </div>
    )
  }

  return (
    <div className="w-full relative">
      {tab.rows.map(row =>
        <StatementMatchResultRow
          key={row.transaction_id}
          row={row}
          account={accountsById.get(tab.accountId)}
          amount={tab.draftAmounts[row.transaction_id] ?? null}
          onAmountChange={amount => onAmountChange(row.transaction_id, amount)}
        />
      )}
    </div>
  )
}

export default StatementMatchTabContent
