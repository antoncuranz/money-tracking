import './App.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";

import {useEffect, useState} from "react";
import TransactionTable from "@/components/TransactionTable.tsx";
import CreditTable from "@/components/CreditTable.tsx";
import CreditTransactionDialog from "@/components/CreditTransactionDialog.tsx";
import TellerButton from "@/components/TellerButton.tsx";
import ActualButton from "@/components/ActualButton.tsx";
import DueDateCalendar from "@/components/DueDateCalendar.tsx";
import AccountSelector from "@/components/AccountSelector.tsx";
import WidgetContainer from "@/components/WidgetContainer.tsx";
import CardBalance from "@/components/CardBalance.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import TxSaveButton from "@/components/TxSaveButton.tsx";

const TransactionPage = () => {
  const [currentAccount, setCurrentAccount] = useState<Account|null>(null)

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [credits, setCredits] = useState<Credit[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([])
  const [balances, setBalances] = useState<Balances|null>();

  const [creditSelection, setCreditSelection] = useState<number|null>(null)
  const [transactionSelection, setTransactionSelection] = useState<Transaction|null>()
  const [transactionAmounts, setTransactionAmounts] = useState<{[id: number]: number|null}>({});
  const [ctDialogOpen, setCtDialogOpen] = useState(false)
  
  const isMobile = false;

  useEffect(() => {
    initAccounts()
  }, []);
  async function initAccounts() {
    const accountResponse = await fetch("/api/accounts")
    const accounts = await accountResponse.json() as Account[]
    setAccounts(accounts)
    setCurrentAccount(accounts[0])
  }

  useEffect(() => {
    updateData()
  }, [currentAccount]);
  async function updateData() {
    if (!currentAccount) return;

    const txResponse = await fetch("/api/transactions?paid=false&account=" + currentAccount.id)
    const transactions = await txResponse.json() as Transaction[]
    setTransactions(transactions.filter(tx => tx.status != 3))
    setTransactionAmounts(Object.fromEntries(transactions.map(tx => [tx.id, tx.amount_eur])))

    const creditResponse = await fetch("/api/credits?usable=true&account=" + currentAccount.id)
    const credits = await creditResponse.json() as Credit[]
    setCredits(credits)

    const balancesResponse = await fetch("/api/balance")
    const balances = await balancesResponse.json() as Balances
    setBalances(balances)
  }

  function updateTransactionAmount(txId: number, newAmount: number|null) {
    const transactionToUpdate = transactions.find(tx => tx.id == txId)
    if (!transactionToUpdate)
      return;

    transactionToUpdate.amount_eur = newAmount
    setTransactions(transactions.map(tx => tx.id == txId ? transactionToUpdate! : tx))
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
      updateData()
  }
  
  function setCurrentAccountById(id: string) {
    const acct = accounts.find(a => a.id == parseInt(id))
    if (acct)
      setCurrentAccount(acct)
  }

  return (
    <>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          {currentAccount &&
            <div className="flex justify-between">
              <AccountSelector accounts={accounts} currentAccountId={currentAccount.id} isMobile={isMobile}
                               onValueChange={setCurrentAccountById}/>
              <div className="flex items-center gap-2">
                <TellerButton account={currentAccount} updateData={updateData}/>
                <ActualButton account={currentAccount} updateData={updateData}/>
                <TxSaveButton transactions={transactions} transactionAmounts={transactionAmounts}/>
              </div>
            </div>
          }
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
                  <Card className="mb-2">
                    <CardHeader className="pb-0">
                      <CardTitle>Credits</CardTitle>
                      <CardDescription/>
                    </CardHeader>
                    <CardContent>
                      <CreditTable credits={credits} selectedCredit={creditSelection}
                                   selectCredit={setCreditSelection}
                                   unselectCredit={() => setCreditSelection(null)}/>
                    </CardContent>
                  </Card>
              }
              <Card className={creditSelection == null ? "mb-2" : "mb-2 outline"}>
                <CardHeader className="pb-0">
                  <CardTitle>Transactions</CardTitle>
                  <CardDescription/>
                </CardHeader>
                <CardContent>
                  <TransactionTable transactions={transactions} updateTransactionAmount={updateTransactionAmount}
                                    readonly={creditSelection != null} selectable={creditSelection != null}
                                    onTransactionClick={openCreditTransactionDialog}/>
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

export default TransactionPage