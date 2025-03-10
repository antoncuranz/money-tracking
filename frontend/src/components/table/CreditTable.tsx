"use client"

import {Account, Credit} from "@/types.ts";
import CreditRow from "@/components/table/CreditRow.tsx";
import {useStore} from "@/store.ts";

interface Props {
  credits: Credit[],
  accounts: Account[],
}

const CreditTable = ({credits, accounts}: Props) => {
  const { creditSelection, setCreditSelection, currentAccount } = useStore()

  function getFilteredCredits() {
    return credits.filter(tx => currentAccount == null || tx.account_id == currentAccount.id)
  }

  return (
    <div className="w-full relative card-table-needs-content">
      {getFilteredCredits().map(credit =>
        <CreditRow key={credit.id} credit={credit} selected={creditSelection?.id == credit.id} disabled={creditSelection != null}
                   selectCredit={() => setCreditSelection(credit, accounts)} unselectCredit={() => setCreditSelection(null, accounts)}
                   account={accounts.find(a => a.id == credit.account_id)}/>
      )}
    </div>
  )
}

export default CreditTable