import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import PaymentRow from "@/components/PaymentRow.tsx";

interface Props {
  payments: any[],
  showAccount?: boolean,
}

const PaymentTable = ({payments, showAccount=false}: Props) => {

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
          <TableHead style={{width: "200px", textAlign: "right"}}>Amount (USD)</TableHead>
          <TableHead style={{width: "200px", textAlign: "right"}}>Amount (EUR)</TableHead>
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Actions</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {payments.map(payment =>
          <PaymentRow key={payment["id"]} payment={payment} showAccount={showAccount}/>
        )}
      </TableBody>
    </Table>
  )
}

export default PaymentTable