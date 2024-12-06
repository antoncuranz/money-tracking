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
    <div className="w-full relative">
      {credits.map(credit =>
        <CreditRow key={credit.id} credit={credit} selected={selectedCredit == credit.id} disabled={selectedCredit != null}
                   selectCredit={() => selectCredit(credit.id)} unselectCredit={unselectCredit}
                   account={accounts.find(a => a.id == credit.account_id)}/>
      )}
    </div>
  )
}

export default CreditTable