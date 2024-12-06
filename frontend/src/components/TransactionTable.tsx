import TransactionRow from "@/components/TransactionRow.tsx";
import {useEffect, useRef, useState} from "react";

interface Props {
  transactions: Transaction[],
  accounts: Account[],
  updateTransactionAmount: (txId: number, newAmount: number|null) => void,
  onTransactionClick: (tx: Transaction) => void,
  readonly?: boolean,
  selectable?: boolean,
}

const TransactionTable = ({transactions, accounts, updateTransactionAmount, onTransactionClick, readonly=true, selectable=false}: Props) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState("auto");

  useEffect(() => {
    if (containerRef.current) {
      const childrenHeight = containerRef.current.scrollHeight;
      setHeight(childrenHeight + "px");
    }
  }, [transactions]);

  return (
    <div ref={containerRef} className="w-full relative" style={{height: height}}>
      {transactions.map(tx =>
        <TransactionRow key={tx.id} transaction={tx} updateTransactionAmount={updateTransactionAmount} account={accounts.find(a => a.id == tx.account_id)}
                        readonly={readonly} selectable={selectable} onClick={() => onTransactionClick ? onTransactionClick(tx) : {}}/>
      )}
    </div>
  )
}

export default TransactionTable