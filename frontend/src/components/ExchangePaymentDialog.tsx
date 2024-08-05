import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {useEffect, useState} from "react";
import AmountInput from "@/components/AmountInput.tsx";
import {useToast} from "@/components/ui/use-toast.ts";

interface Props {
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
  payment: any,
  exchange: number,
}

const ExchangePaymentDialog = ({open, onClose, payment, exchange}: Props) => {
  const [amount, setAmount] = useState<number>(null)

  const { toast } = useToast();

  useEffect(() => {
    initData()
  }, [payment]);
  async function initData() {
    if (!payment)
      return

    const ep = payment["exchangepayment_set"].find(ep => ep["exchange"]["id"] == exchange)
    setAmount(ep ? ep["amount"] : null)
  }

  function onClearButtonClick() {
    updateExchangePayment(0)
  }

  function onSaveButtonClick() {
    updateExchangePayment(amount ?? 0)
  }

  async function updateExchangePayment(newAmount: number) {
    const url = "/api/exchanges/" + exchange + "?amount=" + newAmount + "&payment=" + payment["id"]
    const response = await fetch(url, {method: "PUT"})
    if (response.ok)
      onClose(true)
    else toast({
      title: "Error updating ExchangePayment",
      description: response.statusText
    })
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Apply Exchange to Payment</DialogTitle>
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
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ExchangePaymentDialog