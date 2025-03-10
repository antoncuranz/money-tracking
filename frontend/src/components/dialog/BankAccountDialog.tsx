import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {useEffect, useState} from "react";
import {Input} from "@/components/ui/input.tsx";
import {BankAccount, PlaidConnection} from "@/types.ts";
import {useToast} from "@/components/ui/use-toast.ts";
import PlaidAccountSelector from "@/components/dialog/PlaidAccountSelector.tsx";

export default function BankAccountDialog({
  open, onClose, connections, bank_account
}: {
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
  connections: PlaidConnection[],
  bank_account?: BankAccount | null
}) {
  const [name, setName] = useState("")
  const [institution, setInstitution] = useState("")
  const [icon, setIcon] = useState("")
  const [plaidAccountId, setPlaidAccountId] = useState<number|null>(null)

  const { toast } = useToast();
  
  useEffect(() => {
    setName(bank_account?.name ?? "")
    setInstitution(bank_account?.institution ?? "")
    setIcon(bank_account?.icon ?? "")
    setPlaidAccountId(null) // TODO
  }, [bank_account])

  async function onSaveButtonClick() {
    const url = bank_account ? "/api/bank_accounts/" + bank_account.id : "/api/bank_accounts"
    const method = bank_account ? "PUT" : "POST"
    
    const response = await fetch(url, {
      method: method,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        name: name,
        institution: institution,
        icon: icon.length > 0 ? icon : null,
        // plaid_account_id: plaidAccountId // TODO!
      })
    })

    if (response.ok)
      onClose(true)
    else toast({
      title: "Error creating BankAccount",
      description: response.statusText
    })
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{bank_account ? "Edit" : "Add"} Bank Account</DialogTitle>
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
              Plaid Connection
            </Label>
            <PlaidAccountSelector connections={connections} value={plaidAccountId} onValueChange={setPlaidAccountId}/>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
