"use client"

import {getSaveErrorDescription, saveTransactionAmounts} from "@/components/buttons/saveAmounts.ts";
import {Button} from "@/components/ui/button.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {TransactionAmountMap} from "@/types.ts";
import {LoaderCircle, Save} from "lucide-react";
import {useRouter} from "next/navigation";
import {useState} from "react";

interface Props {
  amounts: TransactionAmountMap;
  onSuccess?: () => void;
  showPartialSaveWarning?: boolean;
}

const SaveAmountsButton = ({amounts, onSuccess, showPartialSaveWarning = false}: Props) => {
  const [inProgress, setInProgress] = useState(false)
  const {toast} = useToast()
  const router = useRouter()

  async function onClick() {
    setInProgress(true)

    const savedSuccessfully = await saveTransactionAmounts(amounts, (txId, partialSave) => {
      toast({
        title: "Error updating transaction " + txId,
        description: getSaveErrorDescription(showPartialSaveWarning, partialSave),
      })
    })

    setInProgress(false)

    if (savedSuccessfully) {
      onSuccess?.()
      router.refresh()
    }
  }

  if (Object.keys(amounts).length === 0)
    return null

  return (
    <Button size="sm" className="h-8 gap-1" onClick={onClick} disabled={inProgress}>
      {inProgress ?
        <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
        :
        <Save className="h-3.5 w-3.5"/>
      }
      <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Save Amounts</span>
    </Button>
  )
}

export default SaveAmountsButton
