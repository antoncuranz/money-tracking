import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import ExchangeRow from "@/components/ExchangeRow.tsx";

interface Props {
  exchanges: any[],
}

const ExchangeTable = ({exchanges}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          <TableHead>Exchange rate</TableHead>
          <TableHead style={{width: "200px", textAlign: "right"}}>Amount (USD)</TableHead>
          <TableHead style={{width: "200px", textAlign: "right"}}>Amount (EUR)</TableHead>
          <TableHead style={{width: "120px"}}>
            <span className="sr-only">Actions</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {exchanges.map(exchange =>
          <ExchangeRow key={exchange["id"]} exchange={exchange}/>
        )}
      </TableBody>
    </Table>
  )
}

export default ExchangeTable