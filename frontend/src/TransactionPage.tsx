import './App.css'
import {Button} from "@/components/ui/button.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {LoaderCircle, Save} from 'lucide-react';

import {useToast} from "@/components/ui/use-toast.ts";
import {useEffect, useState} from "react";
import TransactionTable from "@/components/TransactionTable.tsx";
import CreditTable from "@/components/CreditTable.tsx";
import CreditTransactionDialog from "@/components/CreditTransactionDialog.tsx";
import TellerButton from "@/components/TellerButton.tsx";
import ActualButton from "@/components/ActualButton.tsx";

const TransactionPage = () => {
  const [currentAccount, setCurrentAccount] = useState<Account|null>(null)

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [credits, setCredits] = useState<Credit[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([])

  const [creditSelection, setCreditSelection] = useState<number|null>(null)
  const [transactionSelection, setTransactionSelection] = useState<Transaction|null>()
  const [transactionAmounts, setTransactionAmounts] = useState<{[id: number]: number|null}>({});
  const [ctDialogOpen, setCtDialogOpen] = useState(false)

  const [saveInProgress, setSaveInProgress] = useState(false)

  const { toast } = useToast();

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
  }

  async function onSaveButtonClick() {
    setSaveInProgress(true)

    const updatedTransactions = transactions.filter(tx => tx.amount_eur != transactionAmounts[tx.id])
    console.log("updatedTransactions", updatedTransactions)

    if (updatedTransactions.length == 0)
      toast({title: "Nothing to do."})

    for (const tx of updatedTransactions) {
      const amount = tx.amount_eur ?? "";
      const response = await fetch("/api/transactions/" + tx.id + "?amount_eur=" + amount, {method: "PUT"})
      if (response.status != 200) {
        toast({title: "Error updating transaction " + tx.id})
        break;
      }
    }

    setSaveInProgress(false)
  }

  function updateTransactionAmount(txId: number, newAmount: number|null) {
    let transactionToUpdate = transactions.find(tx => tx.id == txId)
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

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
            <Tabs value={currentAccount ? currentAccount.id.toString() : "-1"}>
              <TabsList>
                {accounts.map(account =>
                  <TabsTrigger className="pl-2" key={account.id} value={account.id.toString()} onClick={() => setCurrentAccount(account)}>
                    {account.name == "Savor" ?
                      <img className="h-5 mr-2" src="https://ecm.capitalone.com/WCM/card/products/new-savor-card-art.png"/>
                    :
                      <img className="h-5 mr-2" src="https://icm.aexp-static.com/Internet/Acquisition/US_en/AppContent/OneSite/category/cardarts/gold-delta-skymiles.png"/>
                    }
                    {account.name}
                  </TabsTrigger>
                )}
              </TabsList>
            </Tabs>
            <div className="ml-auto flex items-center gap-2">
              { currentAccount &&
                <>
                  <TellerButton account={currentAccount} updateData={updateData}/>
                  <ActualButton account={currentAccount} updateData={updateData}/>
                  <Button size="sm" className="h-8 gap-1" onClick={onSaveButtonClick} disabled={saveInProgress}>
                    { saveInProgress ?
                      <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
                    :
                      <Save className="h-3.5 w-3.5"/>
                    }
                    <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                      Save Amounts
                    </span>
                  </Button>
                </>
              }
            </div>
          </div>
          { credits.length > 0 &&
            <Card className="mb-2">
              <CardHeader className="pb-0">
                <CardTitle>Credits</CardTitle>
                <CardDescription/>
              </CardHeader>
              <CardContent>
                <CreditTable credits={credits} selectedCredit={creditSelection} selectCredit={setCreditSelection} unselectCredit={() => setCreditSelection(null)}/>
              </CardContent>
            </Card>
          }
          { transactions.length > 0 &&
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
          }
        </main>
      </div>
      <CreditTransactionDialog open={ctDialogOpen} onClose={onDialogClose} credit={creditSelection!} transaction={transactionSelection!}/>
  </>
)
}

export default TransactionPage