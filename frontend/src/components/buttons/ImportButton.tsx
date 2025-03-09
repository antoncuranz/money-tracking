"use client"

import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Plug} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import {useStore} from "@/store.ts";

const ImportButton = () => {
  const [inProgress, setInProgress] = useState(false)

  const { currentAccount } = useStore()
  const router = useRouter()
  const { toast } = useToast()

  async function onButtonClick() {
    setInProgress(true)

    const url = "/api/import/" + currentAccount!["id"]
    const response = await fetch(url, {method: "POST"})

    if (!response.ok) {
      toast({
        title: "Error importing Transactions",
        description: response.statusText
      })
    }

    router.refresh()
    setInProgress(false)
  }

  return (
    <>
      {currentAccount &&
        <Button size="sm" className="h-8 gap-1" onClick={() => onButtonClick()} disabled={inProgress}>
          { inProgress ?
            <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
          :
            <Plug className="h-3.5 w-3.5"/>
          }
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
          Data Import
          </span>
        </Button>
      }
    </>
  )
}

export default ImportButton