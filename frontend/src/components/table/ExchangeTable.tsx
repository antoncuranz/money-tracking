import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import {Exchange} from "@/types.ts";
import ExchangeRow from "@/components/table/ExchangeRow.tsx";

interface Props {
  exchanges: Exchange[],
  selectedExchange: number|null,
  selectExchange: (id: number) => void,
  unselectExchange: () => void,
  deleteExchange: (id: number) => void,
}

const ExchangeTable = ({exchanges, selectedExchange=null, selectExchange, unselectExchange, deleteExchange}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          <TableHead>Exchange rate</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (USD)</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (EUR)</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Paid (EUR)</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Fees (EUR)</TableHead>
          <TableHead style={{width: "120px"}}>
            <span className="sr-only">Actions</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {exchanges.map(exchange =>
          <ExchangeRow key={exchange["id"]} exchange={exchange} selected={selectedExchange == exchange["id"]} disabled={selectedExchange != null}
                       selectExchange={() => selectExchange(exchange["id"])} deleteExchange={() => deleteExchange(exchange["id"])}
                       unselectExchange={unselectExchange}/>
        )}
      </TableBody>
    </Table>
  )
}

export default ExchangeTable