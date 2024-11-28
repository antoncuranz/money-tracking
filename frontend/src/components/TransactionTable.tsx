import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import TransactionRow from "@/components/TransactionRow.tsx";

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
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "160px"}}>Date</TableHead>
          <TableHead>Counterparty</TableHead>
          <TableHead>Description</TableHead>
          <TableHead style={{width: "100px"}}>Category</TableHead>
          <TableHead className="text-right" style={{width: "150px"}}>Amount (USD)</TableHead>
          <TableHead className="text-right" style={{width: "150px"}}>Amount (EUR)</TableHead>
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Status</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map(tx =>
          <TransactionRow key={tx.id} transaction={tx} updateTransactionAmount={updateTransactionAmount} account={accounts.find(a => a.id == tx.account_id)}
                          readonly={readonly} selectable={selectable} onClick={() => onTransactionClick ? onTransactionClick(tx) : {}}/>
        )}
      </TableBody>
    </Table>
  )
}

export default TransactionTable