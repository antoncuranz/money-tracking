"use client"

import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {Account} from "@/types.ts";
import {useResponsiveState} from "@/components/ResponsiveStateProvider.tsx";
import {useSelectionState} from "@/components/SelectionStateProvider.tsx";

interface Props {
  accounts: Account[],
}

const AccountSelector = ({accounts}: Props) => {
  const { currentAccount, setCurrentAccount } = useSelectionState()
  const { isMobile } = useResponsiveState()

  function setCurrentAccountById(id: string) {
    const acct = accounts.find(a => a.id == parseInt(id))
    setCurrentAccount(acct ?? null)
  }

  function getAccountId() {
    return currentAccount?.id ?? -1
  }

  return (
    <>
      {isMobile ?
          <Select value={getAccountId().toString()} onValueChange={setCurrentAccountById}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select an account"/>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="-1">All</SelectItem>
                {accounts.map(account =>
                    <SelectItem key={account.id} value={account.id.toString()}>{account.name}</SelectItem>
                )}
              </SelectGroup>
            </SelectContent>
          </Select>
        :
          <Tabs value={getAccountId().toString()} onValueChange={setCurrentAccountById}>
            <TabsList>
              <TabsTrigger className="pl-2" value="-1">All</TabsTrigger>
              {accounts.map(account =>
                  <TabsTrigger className="pl-2" key={account.id} value={account.id.toString()}>
                    <img className="h-5 mr-2" src={account.icon} alt=""/>
                    {account.name}
                  </TabsTrigger>
              )}
            </TabsList>
          </Tabs>
      }
    </>
  )
}

export default AccountSelector