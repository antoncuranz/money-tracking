import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {useEffect, useState} from "react";
import AmountInput from "@/components/AmountInput.tsx";
import {useToast} from "@/components/ui/use-toast.ts";

interface Props {
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
  transaction: any,
  credit: number,
}

const CreditTransactionDialog = ({open, onClose, transaction, credit}: Props) => {
  const [amount, setAmount] = useState<number>(null)

  const { toast } = useToast();

  useEffect(() => {
    initData()
  }, [transaction]);
  async function initData() {
    if (!transaction)
      return

    const ct = transaction["credittransaction_set"].find(ct => ct["credit"]["id"] == credit)
    setAmount(ct ? ct["amount"] : null)
  }

  function onClearButtonClick() {
    updateCreditTransaction(0)
  }

  function onMaximumButtonClick() {
    alert("TODO")
    // also disable credit selection mode in ImportPage
  }

  function onSaveButtonClick() {
    updateCreditTransaction(amount ?? 0)
  }

  async function updateCreditTransaction(newAmount: number) {
    const url = "/api/credits/" + credit + "?amount=" + newAmount + "&transaction=" + transaction["id"]
    const response = await fetch(url, {method: "PUT"})
    if (response.ok)
      onClose(true)
    else toast({
      title: "Error updating CreditTransaction",
      description: response.statusText
    })
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Apply Credit to Transaction</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="amount_eur" className="text-right">
              Amount
            </Label>
            <AmountInput
              id="amount_eur"
              className="col-span-3"
              amount={amount}
              setAmount={setAmount}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClearButtonClick}>Clear</Button>
          <Button variant="outline" onClick={onMaximumButtonClick}>Maximum</Button>
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreditTransactionDialog