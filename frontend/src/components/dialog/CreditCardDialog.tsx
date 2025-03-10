import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {useEffect, useState} from "react";
import AmountInput from "@/components/dialog/AmountInput.tsx";
import {Input} from "@/components/ui/input.tsx";
import PlaidAccountSelector from "@/components/dialog/PlaidAccountSelector.tsx";
import BankAccountSelector from "@/components/dialog/BankAccountSelector.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {Account, BankAccount, PlaidConnection} from "@/types.ts";

export default function CreditCardDialog({
  connections, bank_accounts, open, onClose, account
}: {
  connections: PlaidConnection[],
  bank_accounts: BankAccount[],
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
  account?: Account | null
}) {
  const [name, setName] = useState("")
  const [institution, setInstitution] = useState("")
  const [icon, setIcon] = useState("")
  const [color, setColor] = useState("")
  const [actualId, setActualId] = useState("")
  const [dueDay, setDueDay] = useState<number|null>(null)
  const [offset, setOffset] = useState<number|null>(null)
  const [targetSpend, setTargetSpend] = useState<number|null>(null)
  const [bankAccountId, setBankAccountId] = useState<number|null>(null)
  const [plaidAccountId, setPlaidAccountId] = useState<number|null>(null)

  const { toast } = useToast();
  
  useEffect(() => {
    setName(account?.name ?? "")
    setInstitution(account?.institution ?? "")
    setIcon(account?.icon ?? "")
    setColor(account?.color ?? "")
    setActualId(account?.actual_id ?? "")
    setDueDay(account?.due_day ?? null)
    setOffset(account?.autopay_offset ?? null)
    setTargetSpend(account?.target_spend ?? null)
    setBankAccountId(account?.bank_account_id ?? null)
    setPlaidAccountId(account?.plaid_account_id ?? null)
  }, [account])

  async function onSaveButtonClick() {
    const url = account ? "/api/accounts/" + account.id : "/api/accounts"
    const method = account ? "PUT" : "POST"
    
    const response = await fetch(url, {
      method: method,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        name: name,
        institution: institution,
        due_day: dueDay,
        autopay_offset: offset,
        icon: icon.length > 0 ? icon : null,
        color: color.length > 0 ? color : null,
        target_spend: targetSpend,
        bank_account_id: bankAccountId,
        plaid_account_id: plaidAccountId,
        actual_id: actualId.length > 0 ? actualId : null,
      })
    })

    if (response.ok)
      onClose(true)
    else toast({
      title: "Error creating Account",
      description: response.statusText
    })
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{account ? "Edit" : "Add"} Credit Card</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input id="name" value={name} onChange={e => setName(e.target.value)}
                   placeholder="" className="col-span-3"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="institution" className="text-right">
              Institution
            </Label>
            <Input id="institution" value={institution} onChange={e => setInstitution(e.target.value)}
                   placeholder="" className="col-span-3"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="icon" className="text-right">
              Icon
            </Label>
            <Input id="icon" value={icon} onChange={e => setIcon(e.target.value)}
                   placeholder="" className="col-span-3"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="color" className="text-right">
              Color
            </Label>
            <Input id="color" value={color} onChange={e => setColor(e.target.value)}
                   placeholder="" className="col-span-3"/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="due_day" className="text-right">
              Due day
            </Label>
            <AmountInput
              id="due_day"
              className="col-span-3"
              amount={dueDay}
              updateAmount={setDueDay}
              decimals={0}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="offset" className="text-right">
              Offset
            </Label>
            <AmountInput
              id="offset"
              className="col-span-3"
              amount={offset}
              updateAmount={setOffset}
              decimals={0}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="target_spend" className="text-right">
              Target Spend
            </Label>
            <AmountInput
              id="target_spend"
              className="col-span-3"
              amount={targetSpend}
              updateAmount={setTargetSpend}
              decimals={0}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="color" className="text-right">
              Bank Account
            </Label>
            <BankAccountSelector bank_accounts={bank_accounts} value={bankAccountId} onValueChange={setBankAccountId}/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="color" className="text-right">
              Plaid Connection
            </Label>
            <PlaidAccountSelector connections={connections} value={plaidAccountId} onValueChange={setPlaidAccountId}/>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="actual_id" className="text-right">
              Actual ID
            </Label>
            <Input id="actual_id" value={actualId} onChange={e => setActualId(e.target.value)}
                   placeholder="" className="col-span-3"/>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
