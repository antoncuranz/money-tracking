import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import PaymentRow from "@/components/PaymentRow.tsx";

interface Props {
  payments: any[],
  showAccount?: boolean,
  selectable?: boolean,
  onPaymentClick?: (tx) => void,
}

const PaymentTable = ({payments, showAccount=false, selectable=false, onPaymentClick=null}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          { showAccount &&
            <TableHead>Account</TableHead>
          }
          <TableHead>Counterparty</TableHead>
          <TableHead>Description</TableHead>
          <TableHead style={{width: "200px"}}>Category</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (USD)</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (EUR)</TableHead>
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Actions</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {payments.map(payment =>
          <PaymentRow key={payment["id"]} payment={payment} showAccount={showAccount} selectable={selectable}
                      onClick={() => onPaymentClick ? onPaymentClick(payment) : {}}/>
        )}
      </TableBody>
    </Table>
  )
}

export default PaymentTable