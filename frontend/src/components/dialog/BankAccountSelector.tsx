import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select.tsx";
import {BankAccount} from "@/types.ts";

export default function BankAccountSelector({
  bank_accounts, value, onValueChange
}: {
  bank_accounts: BankAccount[],
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
          {bank_accounts.map(bank_account =>
            <SelectItem key={bank_account.id} value={bank_account.id.toString()}>{bank_account.name}</SelectItem>
          )}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
