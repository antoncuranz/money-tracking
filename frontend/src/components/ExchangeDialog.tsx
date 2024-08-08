import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {Calendar} from "@/components/ui/calendar.tsx";
import {CalendarIcon, Coins} from "lucide-react";
import {useState} from "react";
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import AmountInput from "@/components/AmountInput.tsx";
import {useToast} from "@/components/ui/use-toast.ts";

interface Props {
  open: boolean,
  onClose: (needsUpdate: boolean) => void,
}

const ExchangeDialog = ({open, onClose}: Props) => {
  const [date, setDate] = useState<Date>()
  const [amountUsd, setAmountUsd] = useState<number>(null)
  const [amountEur, setAmountEur] = useState<number>(null)
  const [exchangeRate, setExchangeRate] = useState<number>(null)

  const { toast } = useToast();

  async function onSaveButtonClick() {
    const response = await fetch("/api/exchanges", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        date: date?.toJSON().substring(0,10),
        amount_usd: amountUsd,
        amount_eur: amountEur,
        exchange_rate: exchangeRate
      })
    })

    if (response.ok)
      onClose(true)
    else toast({
      title: "Error creating Exchange",
      description: response.statusText
    })
  }

  return (
    <Dialog open={open} onOpenChange={open => !open ? onClose(false) : {}}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Exchange</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="date" className="text-right">
              Date
            </Label>
            <Popover id="date">
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-[280px] justify-start text-left font-normal",
                    !date && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4"/>
                  {date ? format(date, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="amount_eur" className="text-right">
              Amount (EUR)
            </Label>
            <AmountInput
              id="amount_eur"
              className="col-span-3"
              amount={amountEur}
              setAmount={setAmountEur}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="amount_usd" className="text-right">
              Amount (USD)
            </Label>
            <AmountInput
              id="amount_usd"
              className="col-span-3"
              amount={amountUsd}
              setAmount={setAmountUsd}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="rate" className="text-right">
              Exchange Rate
            </Label>
            <AmountInput
              id="rate"
              className="col-span-3"
              amount={exchangeRate}
              setAmount={setExchangeRate}
              decimals={7}
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={onSaveButtonClick}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ExchangeDialog