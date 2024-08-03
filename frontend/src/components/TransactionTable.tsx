import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import TransactionRow from "@/components/TransactionRow.tsx";

interface Props {
  transactions: any[],
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
}

const TransactionTable = ({transactions, updateTransactionAmount=null, readonly=true}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          <TableHead>Counterparty</TableHead>
          <TableHead>Description</TableHead>
          <TableHead style={{width: "200px"}}>Category</TableHead>
          <TableHead style={{width: "200px", textAlign: "right"}}>Amount (USD)</TableHead>
          {transactions.length > 0 && transactions[0]["amount_eur"] &&
            <TableHead style={{width: "200px", textAlign: "right"}}>Amount (EUR)</TableHead>
          }
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Status</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map(tx =>
          <TransactionRow key={tx["id"]} transaction={tx} readonly={readonly} updateTransactionAmount={updateTransactionAmount}/>
        )}
      </TableBody>
    </Table>
  )
}

export default TransactionTable