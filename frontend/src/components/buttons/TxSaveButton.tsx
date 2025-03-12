"use client"

import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Save} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import {useStore} from "@/store.ts";

const TxSaveButton = () => {
  const [inProgress, setInProgress] = useState(false)
  const { changedTransactionAmounts, clearTransactionAmounts } = useStore()
  const router = useRouter()
  const { toast } = useToast();

  async function onClick() {
    setInProgress(true)

    console.log("transactionAmounts", changedTransactionAmounts)

    let savedSuccessfully = true
    for (const [txId, amount] of Object.entries(changedTransactionAmounts)) {
      const response = await fetch("/api/transactions/" + txId + (amount != null ? "?amount_eur=" + amount : ""), {method: "PUT"})

      if (!response.ok) {
        toast({title: "Error updating transaction " + txId})
        savedSuccessfully = false;
        break;
      }
    }

    setInProgress(false)
    if (savedSuccessfully) {
      clearTransactionAmounts()
      router.refresh()
    }
  }

  return (
    <>
      {Object.keys(changedTransactionAmounts).length > 0 &&
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
      }
    </>
  )
}

export default TxSaveButton