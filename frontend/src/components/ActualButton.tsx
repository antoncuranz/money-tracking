"use client"

import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {Import, LoaderCircle} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import {useSelectionState} from "@/components/SelectionStateProvider.tsx";

const ActualButton = () => {
  const [inProgress, setInProgress] = useState(false)
  const { currentAccount } = useSelectionState()
  const router = useRouter()
  const { toast } = useToast();

  async function onClick() {
    setInProgress(true)

    const response = await fetch("/api/actual/" + currentAccount!.id, {method: "POST"})

    if (!response.ok) {
      toast({
        title: "Error during Actual import",
        description: response.statusText
      })
    }

    router.refresh()
    setInProgress(false)
  }

  return (
    <>
      {currentAccount &&
        <Button size="sm" className="h-8 gap-1" onClick={() => onClick()} disabled={inProgress}>
          { inProgress ?
            <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
          :
            <Import className="h-3.5 w-3.5"/>
          }
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
            Actual Import
          </span>
        </Button>
      }
    </>
  )
}

export default ActualButton