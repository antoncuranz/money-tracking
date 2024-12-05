import {Table, TableBody, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import CreditRow from "@/components/CreditRow.tsx";
import {Account, Credit} from "@/types.ts";

interface Props {
  credits: Credit[],
  accounts: Account[],
  selectedCredit: number|null,
  selectCredit: (id: number) => void,
  unselectCredit: () => void,
}

const CreditTable = ({credits, accounts, selectedCredit, selectCredit, unselectCredit}: Props) => {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead style={{width: "150px"}}>Date</TableHead>
          <TableHead>Counterparty</TableHead>
          <TableHead>Description</TableHead>
          <TableHead style={{width: "200px"}}>Category</TableHead>
          <TableHead className="text-right" style={{width: "200px"}}>Amount (USD)</TableHead>
          <TableHead style={{width: "50px"}}>
            <span className="sr-only">Status</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {credits.map(credit =>
          <CreditRow key={credit.id} credit={credit} selected={selectedCredit == credit.id} disabled={selectedCredit != null}
                     selectCredit={() => selectCredit(credit.id)} unselectCredit={unselectCredit}
                     account={accounts.find(a => a.id == credit.account_id)}/>
        )}
      </TableBody>
    </Table>
  )
}

export default CreditTable