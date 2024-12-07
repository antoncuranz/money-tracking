"use client"

import CreditRow from "@/components/CreditRow.tsx";
import {Account, Credit} from "@/types.ts";
import {useSelectionState} from "@/components/SelectionStateProvider.tsx";

interface Props {
  credits: Credit[],
  accounts: Account[],
}

const CreditTable = ({credits, accounts}: Props) => {
  const { creditSelection, setCreditSelection } = useSelectionState()

  return (
    <div className="w-full relative">
      {credits.map(credit =>
        <CreditRow key={credit.id} credit={credit} selected={creditSelection?.id == credit.id} disabled={creditSelection != null}
                   selectCredit={() => setCreditSelection(credit)} unselectCredit={() => setCreditSelection(null)}
                   account={accounts.find(a => a.id == credit.account_id)}/>
      )}
    </div>
  )
}

export default CreditTable