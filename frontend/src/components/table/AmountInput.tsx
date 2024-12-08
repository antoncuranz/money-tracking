import {FocusEvent, useEffect, useState} from 'react'
import {Input} from "@/components/ui/input.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {formatAmount} from "@/components/util.ts";

interface Props {
  amount: number|null,
  setAmount: (newAmount: number|null) => void,
  className?: string,
  disabled?: boolean,
  decimals?: number,
  id?: string,
}

const AmountInput = ({amount, setAmount, className = "", disabled = false, decimals = 2, id}: Props) => {
  const [stringAmount, setStringAmount] = useState("")
  const { toast } = useToast();

  useEffect(() => {
    updateAmount()
  }, [amount]);
  function updateAmount() {
    setStringAmount(formatAmount(amount, decimals))
  }

  function onBlur(event: FocusEvent<HTMLInputElement>) {
    const newAmount = event.target.value

    try {
      const newValue = newAmount ? parseMonetaryValue(newAmount) : null
      setAmount(newValue)
    } catch (e) {
      toast({title: "Unable to parse amount"})
      updateAmount()
    }
  }

  function parseMonetaryValue(valueString: string) {
    const re = new RegExp(String.raw`^(-)?(\d*)(?:[.,](\d{0,${decimals}}))?\d*$`);
    const match = valueString.replace(/\s/g, "").match(re)

    if (!match || match[2].length + (match[3]?.length ?? 0) == 0)
      throw new Error("Unable to parse value string '" + valueString + "'")

    const sign = match[1] ? -1 : 1
    const euros = parseInt(match[2]) || 0
    let cents = parseInt(match[3]) || 0

    if (match[3])
      cents *= Math.pow(10, decimals - match[3].length)

    return sign * (euros * Math.pow(10, decimals!) + cents)
  }

  return (
    <Input id={id} value={stringAmount} onChange={e => setStringAmount(e.target.value)}
           onBlur={onBlur} className={className + " text-right"} disabled={disabled}/>
  )
}

export default AmountInput