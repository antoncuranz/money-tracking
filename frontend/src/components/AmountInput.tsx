import {useEffect, useState} from 'react'
import {Input} from "@/components/ui/input.tsx";
import {useToast} from "@/components/ui/use-toast.ts";

interface Props {
  amount: number,
  setAmount: (newAmount) => void,
  className?: string,
}

const AmountInput = ({amount, setAmount, className = ""}: Props) => {
  const [stringAmount, setStringAmount] = useState("")
  const { toast } = useToast();

  useEffect(() => {
    updateAmount()
  }, [amount]);

  function updateAmount() {
    setStringAmount(formatAmount(amount))
  }

  function formatAmount(amount: number | null): string {
    if (!amount) return ""
    const sign = amount < 0 ? "-" : ""
    return sign + Math.abs(amount / 100 >> 0).toString().padStart(1, "0") + "," + Math.abs(amount % 100).toString().padStart(2, "0")
  }

  function onBlur(event: any) {
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
    const re = /^(-)?(\d*)(?:[.,](\d{0,2}))?\d*$/
    const match = valueString.replace(/\s/g, "").match(re)

    if (!match || match[2].length + (match[3]?.length ?? 0) == 0)
      throw new Error("Unable to parse value string '" + valueString + "'")

    const sign = match[1] ? -1 : 1
    const euros = parseInt(match[2]) || 0
    let cents = parseInt(match[3]) || 0

    if (match[3]?.length == 1)
      cents *= 10

    return sign * (euros * 100 + cents)
  }

  return (
    <Input value={stringAmount} onChange={e => setStringAmount(e.target.value)}
           onBlur={onBlur} style={{textAlign: "right"}} className={className}/>
  )
}

export default AmountInput