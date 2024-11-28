import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Save} from "lucide-react";
import {useState} from "react";

interface Props {
  transactions: Transaction[],
  transactionAmounts: {[id: number]: number|null},
  updateData?: () => void,
}

const TxSaveButton = ({transactions, transactionAmounts, updateData=() => {}}: Props) => {
  const [inProgress, setInProgress] = useState(false)
  const { toast } = useToast();

  async function onClick() {
    setInProgress(true)

    const updatedTransactions = transactions.filter(tx => tx.amount_eur != transactionAmounts[tx.id])
    console.log("updatedTransactions", updatedTransactions)

    if (updatedTransactions.length == 0)
      toast({title: "Nothing to do."})

    let savedSuccessfully = true
    for (const tx of updatedTransactions) {
      const amount = tx.amount_eur ?? "";
      const response = await fetch("/api/transactions/" + tx.id + "?amount_eur=" + amount, {method: "PUT"})
      if (response.status != 200) {
        toast({title: "Error updating transaction " + tx.id})
        savedSuccessfully = false;
        break;
      }
    }

    setInProgress(false)
    if (savedSuccessfully)
      updateData()
  }

  return (
    <Button size="sm" className="h-8 gap-1" onClick={onClick} disabled={inProgress}>
      {inProgress ?
          <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
          :
          <Save className="h-3.5 w-3.5"/>
      }
      <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
        Save Amounts
      </span>
    </Button>
  )
}

export default TxSaveButton