import {Button} from "@/components/ui/button.tsx";
import {Dialog, DialogFooter, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger} from "@/components/ui/dialog.tsx";
import {Label} from "@/components/ui/label.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {Calendar} from "@/components/ui/calendar.tsx";
import {CalendarIcon, Coins} from "lucide-react";
import {useState} from "react";
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import AmountInput from "@/components/AmountInput.tsx";

interface Props {
  transactions: any[],
  updateTransactionAmount?: (txId: string, newAmount) => void,
  readonly?: boolean,
}

const ExchangeDialog = () => {
  const [date, setDate] = useState<Date>()
  const [amountUsd, setAmountUsd] = useState(0)
  const [amountEur, setAmountEur] = useState(0)
  const [feeEur, setFeeEur] = useState(0)

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm" className="h-8 gap-1">
          <Coins className="h-3.5 w-3.5"/>
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
            Add Exchange
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Exchange</DialogTitle>
          {/*exchange_rate = IntegerField(null=True)  # needs to be IBKR rate*/}

          {/*<DialogDescription>*/}
          {/*  Make changes to your profile here. Click save when you're done.*/}
          {/*</DialogDescription>*/}
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
            <Label htmlFor="fee_eur" className="text-right">
              Exchange Fee (EUR)
            </Label>
            <AmountInput
              id="fee_eur"
              className="col-span-3"
              amount={feeEur}
              setAmount={setFeeEur}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="rate" className="text-right">
              Exchange Rate
            </Label>
            <Input
              id="rate"
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ExchangeDialog