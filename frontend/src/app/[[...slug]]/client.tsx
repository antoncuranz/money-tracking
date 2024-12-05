'use client'

import AccountSelector from "@/components/AccountSelector.tsx";
import TellerButton from "@/components/TellerButton.tsx";
import ActualButton from "@/components/ActualButton.tsx";
import TxSaveButton from "@/components/TxSaveButton.tsx";
import WidgetContainer from "@/components/WidgetContainer.tsx";
import DueDateCalendar from "@/components/DueDateCalendar.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import CardBalance from "@/components/CardBalance.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import CreditTable from "@/components/CreditTable.tsx";
import TransactionTable from "@/components/TransactionTable.tsx";
import CreditTransactionDialog from "@/components/CreditTransactionDialog.tsx";
import {useEffect, useState} from "react";
import {useRouter} from "next/navigation";
import {Account, Transaction, Credit, Balances} from "@/types.ts";

export function ClientOnly({
  accounts,
  transactions,
  credits,
  balances
}: {
  accounts: Account[],
  transactions: Transaction[],
  credits: Credit[],
  balances: Balances,
}) {

  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>(transactions)
  const [currentAccount, setCurrentAccount] = useState<Account|null>(null)
  const [creditSelection, setCreditSelection] = useState<number|null>(null)
  const [transactionSelection, setTransactionSelection] = useState<Transaction|null>()
  const [changedTransactionAmounts, setChangedTransactionAmounts] = useState<{[id: number]: number|null}>({})
  const [ctDialogOpen, setCtDialogOpen] = useState(false)

  const router = useRouter();
  const isMobile = false

  useEffect(() => {
    updateFilteredTransactions()
  }, [currentAccount]);
  function updateFilteredTransactions() {
    setFilteredTransactions(transactions.filter(tx =>
      currentAccount == null || tx.account_id == currentAccount.id)
    )
  }

  function updateTransactionAmount(txId: number, newAmount: number|null) {
    setChangedTransactionAmounts(prevAmounts => ({
      ...prevAmounts,
      [txId]: newAmount
    }));
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

  function setCurrentAccountById(id: string) {
    const acct = accounts.find(a => a.id == parseInt(id))
    setCurrentAccount(acct ?? null)
  }

  function onCreditSelection(creditId: number) {
    const credit = credits.find(c => c.id == creditId)
    if (!credit)
      return

    if (!currentAccount) {
      const acct = accounts.find(a => a.id == credit.account_id)
      if (!acct)
        return
      setCurrentAccount(acct)
    }

    setCreditSelection(creditId)
  }

  return (
    <>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex justify-between">
            <AccountSelector accounts={accounts} currentAccountId={currentAccount?.id ?? -1} isMobile={isMobile}
                             onValueChange={setCurrentAccountById}/>
            <div className="flex items-center gap-2">
              {currentAccount &&
                  <>
                      <TellerButton account={currentAccount} updateData={router.refresh}/>
                      <ActualButton account={currentAccount} updateData={router.refresh}/>
                  </>
              }
              <TxSaveButton changedTransactionAmounts={changedTransactionAmounts} updateData={router.refresh}/>
            </div>
          </div>
          <div className={isMobile ? "gap-2 mb-2" : "flex gap-2 mb-2"}>
            <div className="flex-initial">
              <WidgetContainer widgets={[
                {
                  title: "Calendar",
                  content: <DueDateCalendar/>,
                  hideTitleDesktop: true
                },
                {
                  title: "Balances",
                  content: (<>
                    {balances && accounts.map(account =>
                      <div key={account.id} className="card-balance-container">
                        <Separator className="balance-separator mb-4 mt-4"/>
                        <CardBalance account={account} balances={balances}/>
                      </div>
                    )}
                  </>)
                }
              ]} isMobile={isMobile}/>
            </div>
            <div className="flex-auto">
              {credits.length > 0 &&
                  <Card className="mb-2 overflow-hidden">
                      <CardHeader className="pb-0">
                          <CardTitle>Credits</CardTitle>
                          <CardDescription/>
                      </CardHeader>
                      <CardContent className="p-0">
                          <CreditTable credits={credits} selectedCredit={creditSelection} accounts={accounts}
                                       selectCredit={onCreditSelection}
                                       unselectCredit={() => setCreditSelection(null)}/>
                      </CardContent>
                  </Card>
              }
              <Card className={creditSelection == null ? "mb-2 overflow-hidden" : "mb-2 outline overflow-hidden"}>
                <CardHeader className="pb-0">
                  <CardTitle>Transactions</CardTitle>
                  <CardDescription/>
                </CardHeader>
                <CardContent className="p-0">
                  <TransactionTable transactions={filteredTransactions} updateTransactionAmount={updateTransactionAmount}
                                    readonly={creditSelection != null} selectable={creditSelection != null}
                                    onTransactionClick={openCreditTransactionDialog} accounts={accounts}/>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
      <CreditTransactionDialog open={ctDialogOpen} onClose={onDialogClose} credit={creditSelection!}
                               transaction={transactionSelection!}/>
    </>
  )
}