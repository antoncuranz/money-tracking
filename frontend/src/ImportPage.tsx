import './App.css'
import {Button} from "@/components/ui/button.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {Plug, Import, Save} from 'lucide-react';

import {useToast} from "@/components/ui/use-toast.ts";
import {useTellerConnect} from 'teller-connect-react';
import {useEffect, useState} from "react";
import TransactionTable from "@/components/TransactionTable.tsx";

const ImportPage = () => {
  const [newTransactions, setNewTransactions] = useState([]);
  const [importedTransactions, setImportedTransactions] = useState([]);
  const [accounts, setAccounts] = useState([])
  const [currentAccount, setCurrentAccount] = useState(-1)

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
    getTransactions()
  }, [currentAccount]);
  async function getTransactions() {
    if (currentAccount < 0) return

    const txResponse = await fetch("/api/accounts/" + currentAccount + "/transactions")
    const transactions = await txResponse.json()

    setNewTransactions(transactions.filter(tx => tx.status != 3))
    setImportedTransactions(transactions.filter(tx => tx.status == 3))
  }

  async function onTellerButtonClick(accessToken?: string) {
    let url = "/api/import/" + currentAccount
    if (accessToken)
      url += "?access_token=" + accessToken
    const response = await fetch(url, {method: "POST"})

    if (!accessToken && response.status == 418) // if mfa required: authorize and try again!
      openTeller()

    await getTransactions()
  }

  async function onActualButtonClick() {
    await fetch("/api/actual/" + currentAccount, {method: "POST"})
    await getTransactions()
  }

  async function onSaveButtonClick() {
    for (const tx of newTransactions) {
      const amount = tx["amount_eur"] ? tx["amount_eur"] : "";
      const response = await fetch("/api/accounts/" + currentAccount + "/transactions/" + tx["id"] + "?amount_eur=" + amount, {method: "PUT"})
      if (response.status != 200) {
        toast({title: "Error updating transaction " + tx["id"]})
        break;
      }
    }
  }

  function updateTransactionAmount(txId: string, newAmount: number|null) {
    let transactionToUpdate = newTransactions.find(tx => tx["id"] == txId)
    if (!transactionToUpdate)
      return;

    transactionToUpdate["amount_eur"] = newAmount
    setNewTransactions(newTransactions.map(tx => tx["id"] == txId ? transactionToUpdate : tx))
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
                  Save
                </span>
              </Button>
            </div>
          </div>
          <Card>
            <CardHeader className="pb-0">
              <CardTitle>New Transactions</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              <TransactionTable transactions={newTransactions} updateTransactionAmount={updateTransactionAmount} readonly={false}/>
            </CardContent>
          </Card>
          <Card className="mt-8">
            <CardHeader className="pb-0">
              <CardTitle>Imported Transactions</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
              {/*TODO: only show last 10? transactions here*/}
              <TransactionTable transactions={importedTransactions}/>
            </CardContent>
          </Card>
        </main>
      </div>
  </>
)
}

export default ImportPage