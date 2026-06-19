import AmountInput from "@/components/dialog/AmountInput.tsx";
import TableRow from "@/components/table/TableRow.tsx";
import {hasLargeDeviation} from "@/components/table/transactionRow.ts";
import {formatAmount} from "@/components/util.ts";
import {Account} from "@/types.ts";
import React, {CSSProperties, MouseEventHandler} from "react";

interface Props {
  account?: Account;
  date: string;
  remoteName: string;
  purpose: string;
  amount: number | null;
  placeholderAmount: number | null | undefined;
  onAmountChange: (amount: number | null) => void;
  amountDisabled?: boolean;
  beforeAmountInput?: React.ReactNode;
  afterAmountInput?: React.ReactNode;
  onClick?: MouseEventHandler<HTMLTableRowElement>;
  className?: string;
  style?: CSSProperties;
}

const EditableTransactionRow = ({
  account,
  date,
  remoteName,
  purpose,
  amount,
  placeholderAmount,
  onAmountChange,
  amountDisabled = false,
  beforeAmountInput,
  afterAmountInput,
  onClick,
  className,
  style,
}: Props) => {
  return (
    <TableRow
      onClick={onClick}
      className={className}
      style={style}
      account={account}
      date={date}
      remoteName={remoteName}
      purpose={purpose}
    >
      {beforeAmountInput}
      <AmountInput
        className="w-24 placeholder:opacity-50"
        amount={amount}
        placeholder={formatAmount(placeholderAmount ?? null)}
        updateAmount={onAmountChange}
        disabled={amountDisabled}
        warnPredicate={value => hasLargeDeviation(placeholderAmount, value)}
      />
      {afterAmountInput}
    </TableRow>
  )
}

export default EditableTransactionRow
