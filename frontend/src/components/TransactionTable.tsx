import TransactionRow from "@/components/TransactionRow.tsx";
import {Account, Transaction} from "@/types.ts";

interface Props {
  transactions: Transaction[],
  accounts: Account[],
  updateTransactionAmount: (txId: number, newAmount: number|null) => void,
  onTransactionClick: (tx: Transaction) => void,
  readonly?: boolean,
  selectable?: boolean,
}

const TransactionTable = ({transactions, accounts, updateTransactionAmount, onTransactionClick, readonly=true, selectable=false}: Props) => {
  return (
    <div className="w-full relative">
      {transactions.map(tx =>
        <TransactionRow key={tx.id} transaction={tx} updateTransactionAmount={updateTransactionAmount} account={accounts.find(a => a.id == tx.account_id)}
                        readonly={readonly} selectable={selectable} onClick={() => onTransactionClick ? onTransactionClick(tx) : {}}/>
      )}
    </div>
  )
}

export default TransactionTable