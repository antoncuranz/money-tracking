import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";

interface Props {
  accounts: Account[],
  currentAccountId: number,
  onValueChange?: (value: string) => void,
  isMobile: boolean
}

const AccountSelector = ({accounts, currentAccountId, onValueChange, isMobile}: Props) => {
  
  return (
    <>
      {isMobile ?
          <Select value={currentAccountId.toString()} onValueChange={onValueChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select an account"/>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {accounts.map(account =>
                    <SelectItem key={account.id} value={account.id.toString()}>{account.name}</SelectItem>
                )}
              </SelectGroup>
            </SelectContent>
          </Select>
          :
          <Tabs value={currentAccountId.toString()} onValueChange={onValueChange}>
            <TabsList>
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