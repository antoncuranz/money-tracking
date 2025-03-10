import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select.tsx";
import {PlaidConnection} from "@/types.ts";

export default function PlaidAccountSelector({
  connections, value, onValueChange
}: {
  connections: PlaidConnection[],
  value: number | null,
  onValueChange: (value: number | null) => void
}) {
  
  function privateValue() {
    return (value ?? -1).toString()
  }

  function privateOnValueChange(value: string) {
    const numberValue = parseInt(value)
    onValueChange(numberValue < 0 ? null : numberValue)
  }
  
  return (
    <Select value={privateValue()} onValueChange={privateOnValueChange}>
      <SelectTrigger className="col-span-3">
        <SelectValue/>
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectItem value="-1">Not connected</SelectItem>
          {connections.map(connection =>
            <span key={connection.id}>
              <SelectLabel>{connection.name ?? connection.plaid_item_id}</SelectLabel>
              {connection.plaid_accounts.map(account =>
                <SelectItem key={account.id} value={account.id.toString()}>{account.name}</SelectItem>
              )}
            </span>
          )}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
