"use client"

import SaveAmountsButton from "@/components/buttons/SaveAmountsButton.tsx";
import Card from "@/components/card/Card.tsx";
import StatementMatchSidebar from "@/components/statement-match/StatementMatchSidebar.tsx";
import {createStatementDraftAmounts, getMatchedStatementRows} from "@/components/statement-match/state.ts";
import StatementMatchTabContent from "@/components/statement-match/StatementMatchTabContent.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {Account, StatementMatchResponse, StatementMatchTab} from "@/types.ts";
import {X} from "lucide-react";
import {useMemo, useRef, useState} from "react";

interface Props {
  accounts: Account[];
}

const StatementMatchPageClient = ({accounts}: Props) => {
  const {toast} = useToast()
  const [tabs, setTabs] = useState<StatementMatchTab[]>([])
  const [activeTabId, setActiveTabId] = useState("")
  const [selectedAccountId, setSelectedAccountId] = useState(accounts[0]?.id.toString() ?? "")
  const requestCounter = useRef(0)
  const controllersRef = useRef(new Map<string, AbortController>())

  const accountsById = useMemo(
    () => new Map(accounts.map(account => [account.id, account] as const)),
    [accounts],
  )
  const disabledAccountIds = useMemo(
    () => new Set(tabs.map(tab => tab.accountId)),
    [tabs],
  )
  const activeTab = tabs.find(tab => tab.id === activeTabId) ?? null

  function getNextSelectableAccountId(blockedAccountId: number) {
    return accounts.find(account => account.id !== blockedAccountId && !disabledAccountIds.has(account.id))?.id.toString() ?? ""
  }

  function setTabIfPresent(tabId: string, updater: (tab: StatementMatchTab) => StatementMatchTab) {
    setTabs(currentTabs => {
      const tabIndex = currentTabs.findIndex(tab => tab.id === tabId)
      if (tabIndex === -1)
        return currentTabs

      const nextTabs = [...currentTabs]
      nextTabs[tabIndex] = updater(currentTabs[tabIndex])
      return nextTabs
    })
  }

  function closeTab(tabId: string) {
    controllersRef.current.get(tabId)?.abort()
    controllersRef.current.delete(tabId)

    const tabIndex = tabs.findIndex(tab => tab.id === tabId)
    const nextTabs = tabs.filter(tab => tab.id !== tabId)
    setTabs(nextTabs)

    if (activeTabId !== tabId)
      return

    const nextActiveTab = nextTabs[tabIndex] ?? nextTabs[tabIndex - 1] ?? null
    setActiveTabId(nextActiveTab?.id ?? "")
  }

  function closeActiveTabAfterSave() {
    if (activeTab != null)
      closeTab(activeTab.id)
  }

  async function uploadStatement(accountId: number, file: File) {
    if (disabledAccountIds.has(accountId)) {
      toast({title: "This account already has an open tab"})
      return
    }

    requestCounter.current += 1
    const tabId = `${accountId}-${requestCounter.current}`
    const tab: StatementMatchTab = {
      id: tabId,
      accountId,
      accountName: accountsById.get(accountId)?.name ?? "Account",
      fileName: file.name,
      status: "loading",
      rows: [],
      draftAmounts: {},
    }

    const controller = new AbortController()
    controllersRef.current.set(tabId, controller)

    setTabs(currentTabs => [...currentTabs, tab])
    setActiveTabId(tabId)
    setSelectedAccountId(getNextSelectableAccountId(accountId))

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`/api/statement-match/${accountId}`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      })

      if (!response.ok) {
        const message = (await response.text()) || response.statusText || "Unable to match statement"
        throw new Error(message)
      }

      const payload = await response.json() as StatementMatchResponse
      const rows = getMatchedStatementRows(payload)
      const draftAmounts = createStatementDraftAmounts(rows)

      setTabIfPresent(tabId, currentTab => ({
        ...currentTab,
        status: "ready",
        rows,
        draftAmounts,
        error: undefined,
      }))
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError")
        return

      const message = error instanceof Error ? error.message : "Unable to match statement"
      toast({title: "Error matching statement", description: message})
      setTabIfPresent(tabId, currentTab => ({
        ...currentTab,
        status: "error",
        error: message,
        rows: [],
        draftAmounts: {},
      }))
    } finally {
      controllersRef.current.delete(tabId)
    }
  }

  function updateDraftAmount(tabId: string, transactionId: number, amount: number | null) {
    setTabIfPresent(tabId, currentTab => {
      const nextDraftAmounts = {...currentTab.draftAmounts}

      if (amount == null)
        delete nextDraftAmounts[transactionId]
      else
        nextDraftAmounts[transactionId] = amount

      return {
        ...currentTab,
        draftAmounts: nextDraftAmounts,
      }
    })
  }

  return (
    <Tabs value={activeTabId} onValueChange={setActiveTabId} className="w-full">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="min-w-0 flex-auto">
          {tabs.length > 0 &&
            <div className="overflow-x-auto no-scrollbar">
              <TabsList className="h-auto justify-start">
                {tabs.map(tab =>
                  <div key={tab.id} className="flex items-center">
                    <TabsTrigger value={tab.id} className="max-w-[18rem] pl-2">
                      <span className="truncate">{tab.accountName} • {tab.fileName}</span>
                    </TabsTrigger>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 shrink-0"
                      onClick={event => {
                        event.stopPropagation()
                        closeTab(tab.id)
                      }}
                    >
                      <X className="h-4 w-4"/>
                    </Button>
                  </div>
                )}
              </TabsList>
            </div>
          }
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {activeTab != null &&
            <SaveAmountsButton amounts={activeTab.draftAmounts} onSuccess={closeActiveTabAfterSave} showPartialSaveWarning/>
          }
        </div>
      </div>
      <div className="not-mobile-flex gap-2 mb-2">
        <div className="shrink-0" style={{minWidth: "18.1rem"}}>
          <StatementMatchSidebar
            accounts={accounts}
            selectedAccountId={selectedAccountId}
            onSelectedAccountIdChange={setSelectedAccountId}
            disabledAccountIds={disabledAccountIds}
            onUpload={uploadStatement}
          />
        </div>
        <div className="flex-auto min-w-0">
          <Card title="Matches">
            {tabs.length === 0 ?
              <div className="flex min-h-[24rem] items-center justify-center p-6 text-center text-sm text-muted-foreground">
                Upload a statement PDF to start a review tab.
              </div>
              :
              tabs.map(tab =>
                <TabsContent key={tab.id} value={tab.id} className="mt-0">
                  <StatementMatchTabContent
                    tab={tab}
                    accountsById={accountsById}
                    onAmountChange={(transactionId, amount) => updateDraftAmount(tab.id, transactionId, amount)}
                  />
                </TabsContent>
              )
            }
          </Card>
        </div>
      </div>
    </Tabs>
  )
}

export default StatementMatchPageClient
