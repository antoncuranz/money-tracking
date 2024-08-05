import './App.css'
import {Button} from "@/components/ui/button.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {Plug, Import, Save} from 'lucide-react';

import {useToast} from "@/components/ui/use-toast.ts";
import {useTellerConnect} from 'teller-connect-react';
import {useEffect, useState} from "react";
import TransactionTable from "@/components/TransactionTable.tsx";
import CreditTable from "@/components/CreditTable.tsx";
import CreditTransactionDialog from "@/components/CreditTransactionDialog.tsx";

const ImportPage = () => {
  const [transactions, setTransactions] = useState([]);
  const [credits, setCredits] = useState([]);
  const [accounts, setAccounts] = useState([])
  const [currentAccount, setCurrentAccount] = useState(-1)
  const [creditSelection, setCreditSelection] = useState<number>(null)
  const [transactionSelection, setTransactionSelection] = useState()
  const [ctDialogOpen, setCtDialogOpen] = useState(false)

  const { toast } = useToast();
  const { open: openTeller, ready: isTellerReady } = useTellerConnect({
    applicationId: "snip",
    environment: "sandbox",
    enrollmentId: "snip",
    onSuccess: authorization => {
      toast({
        title: "Teller success",
        description: authorization.accessToken
      })
      onTellerButtonClick(authorization.accessToken)
    },
    onFailure: failure => toast({
      title: "Teller failure",
      description: failure.message
    })
  });

  useEffect(() => {
    initAccounts()
  }, []);
  async function initAccounts() {
    let accountResponse = await fetch("/api/accounts")
    accountResponse = await accountResponse.json()
    setAccounts(accountResponse as any[])
  }

  useEffect(() => {
    updateData()
  }, [currentAccount]);
  async function updateData() {
    if (currentAccount < 0) return

    const txResponse = await fetch("/api/accounts/" + currentAccount + "/transactions")
    const transactions = await txResponse.json()
    setTransactions(transactions.filter(tx => tx.status != 3))

    const creditResponse = await fetch("/api/accounts/" + currentAccount + "/credits")
    const credits = await creditResponse.json()
    // setCredits(credits.filter(c => c.transactions.length == 0))
    setCredits(credits)
  }

  async function onTellerButtonClick(accessToken?: string) {
    let url = "/api/import/" + currentAccount
    if (accessToken)
      url += "?access_token=" + accessToken
    const response = await fetch(url, {method: "POST"})

    if (!accessToken && response.status == 418) // if mfa required: authorize and try again!
      openTeller()

    await updateData()
  }

  async function onActualButtonClick() {
    await fetch("/api/actual/" + currentAccount, {method: "POST"})
    await updateData()
  }

  async function onSaveButtonClick() {
    for (const tx of transactions) {
      const amount = tx["amount_eur"] == null ? "" : tx["amount_eur"];
      const response = await fetch("/api/accounts/" + currentAccount + "/transactions/" + tx["id"] + "?amount_eur=" + amount, {method: "PUT"})
      if (response.status != 200) {
        toast({title: "Error updating transaction " + tx["id"]})
        break;
      }
    }
  }

  function updateTransactionAmount(txId: string, newAmount: number|null) {
    let transactionToUpdate = transactions.find(tx => tx["id"] == txId)
    if (!transactionToUpdate)
      return;

    transactionToUpdate["amount_eur"] = newAmount
    setTransactions(transactions.map(tx => tx["id"] == txId ? transactionToUpdate : tx))
  }

  function openCreditTransactionDialog(tx) {
    if (creditSelection != null) {
      setTransactionSelection(tx)
      setCtDialogOpen(true)
    }
  }

  function onDialogClose(needsUpdate) {
    setCtDialogOpen(false)

    if (needsUpdate)
      updateData()
  }

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all" onClick={() => setCurrentAccount(-1)}>All</TabsTrigger>
                {accounts.map(account =>
                  <TabsTrigger key={account.id} value={account.id} onClick={() => setCurrentAccount(account.id)}>{account.name}</TabsTrigger>
                )}
              </TabsList>
            </Tabs>
            <div className="ml-auto flex items-center gap-2">
              <Button size="sm" className="h-8 gap-1" onClick={() => onTellerButtonClick()} disabled={currentAccount < 0  || !isTellerReady}>
                <Plug className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Teller Connect
                </span>
              </Button>
              <Button size="sm" className="h-8 gap-1" onClick={onActualButtonClick} disabled={currentAccount < 0}>
                <Import className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Actual Import
                </span>
              </Button>
              <Button size="sm" className="h-8 gap-1" onClick={onSaveButtonClick} disabled={currentAccount < 0}>
                <Save className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Save Amounts
                </span>
              </Button>
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
      <CreditTransactionDialog open={ctDialogOpen} onClose={onDialogClose} credit={creditSelection} transaction={transactionSelection}/>
  </>
)
}

export default ImportPage