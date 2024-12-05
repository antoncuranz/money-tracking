import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {useEffect, useState} from "react";
import AmountInput from "@/components/AmountInput.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {Checkbox} from "@/components/ui/checkbox.tsx";
import {Transaction} from "@/types.ts";

interface Props {
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
  transaction: Transaction,
  credit: number,
}

const CreditTransactionDialog = ({open, onClose, transaction, credit}: Props) => {
  const [appliedCredit, setAppliedCredit] = useState<number|null>(null)
  const [adjustedAmt, setAdjustedAmt] = useState<number>(0)
  const [adjustAmt, setAdjustAmt] = useState(true)

  const { toast } = useToast();

  useEffect(() => {
    initData()
  }, [transaction]);
  async function initData() {
    if (!transaction)
      return

    const ct = transaction.credittransaction_set.find(ct => ct.credit.id == appliedCredit)
    setAppliedCredit(ct ? ct.amount : null)
    setAdjustedAmt(transaction.amount_eur ?? 0)
  }

  function onClearButtonClick() {
    setAppliedCredit(0)
    setAdjustedAmt(0)
  }

  function onMaximumButtonClick() {
    alert("TODO")
    // also disable credit selection mode in ImportPage
  }

  async function onSaveButtonClick() {
    const amount = appliedCredit ?? 0;
    const url = "/api/credits/" + credit + "?amount=" + amount + "&transaction=" + transaction.id
    const response = await fetch(url, {method: "PUT"})
    if (!response.ok) {
      toast({
        title: "Error updating CreditTransaction",
        description: response.statusText
      })
      return
    }

    if (adjustAmt) {
      const response = await fetch("/api/transactions/" + transaction.id + "?amount_eur=" + adjustedAmt, {method: "PUT"})
      if (!response.ok)
        toast({
          title: "Error adjusting Transaction amount",
          description: response.statusText
        })
    }

    onClose(true)
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Apply Credit to Transaction</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="credit" className="text-right">
              Credit
            </Label>
            <AmountInput
              id="credit"
              className="col-span-3"
              amount={appliedCredit}
              setAmount={setAppliedCredit}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <div>
              <Checkbox id="adjust_amt" className="float-right" checked={adjustAmt} onCheckedChange={chst => chst != "indeterminate" ? setAdjustAmt(chst) : {}}/>
            </div>
            <Label htmlFor="adjust_amt" className="col-span-3">
              Adjust Amount (EUR) of Transaction
            </Label>
          </div>
          { adjustAmt &&
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="amount_eur" className="text-right">
                  Amount
                </Label>
                <AmountInput
                  id="amount_eur"
                  className="col-span-3"
                  amount={adjustedAmt}
                  setAmount={amt => amt ? setAdjustedAmt(amt) : setAdjustedAmt(0)}
                />
              </div>
            }
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClearButtonClick}>Clear</Button>
          <Button variant="outline" onClick={onMaximumButtonClick} disabled={true}>Maximum</Button>
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreditTransactionDialog