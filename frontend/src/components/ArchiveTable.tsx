import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import ArchiveRow from "@/components/ArchiveRow.tsx";
import {Transaction} from "@/types.ts";

interface Props {
  transactions: Transaction[],
}

const ArchiveTable = ({transactions}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          <TableHead style={{width: "100px"}}>Account</TableHead>
          <TableHead>Counterparty</TableHead>
          <TableHead>Description</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (EUR)</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Fees and Risk (EUR)</TableHead>
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Status</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map(tx =>
          <ArchiveRow key={tx["id"]} transaction={tx}/>
        )}
      </TableBody>
    </Table>
  )
}

export default ArchiveTable