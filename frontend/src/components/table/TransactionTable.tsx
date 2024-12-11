"use client"

import {Account, Transaction} from "@/types.ts";
import {useState} from "react";
import {useRouter} from "next/navigation";
import TransactionRow from "@/components/table/TransactionRow.tsx";
import CreditTransactionDialog from "@/components/dialog/CreditTransactionDialog.tsx";
import {useStore} from "@/store.ts";

interface Props {
  transactions: Transaction[],
  accounts: Account[],
}

const TransactionTable = ({transactions, accounts}: Props) => {
  const [transactionSelection, setTransactionSelection] = useState<Transaction|null>()
  const [ctDialogOpen, setCtDialogOpen] = useState(false)

  const { currentAccount, creditSelection } = useStore()

  const router = useRouter();

  function getFilteredTransactions() {
    return transactions.filter(tx => currentAccount == null || tx.account_id == currentAccount.id)
  }

  function openCreditTransactionDialog(tx: Transaction) {
    if (creditSelection != null) {
      setTransactionSelection(tx)
      setCtDialogOpen(true)
    }
  }

  function onDialogClose(needsUpdate: boolean) {
    setCtDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  return (
    <>
      <div className="w-full relative">
        {getFilteredTransactions().map(tx =>
          <TransactionRow key={tx.id} transaction={tx} account={accounts.find(a => a.id == tx.account_id)}
                          readonly={creditSelection != null} selectable={creditSelection != null} onClick={() => openCreditTransactionDialog(tx)}/>
        )}
      </div>
      <CreditTransactionDialog open={ctDialogOpen} onClose={onDialogClose} credit={creditSelection?.id ?? -1} transaction={transactionSelection!}/>
    </>
  )
}

export default TransactionTable