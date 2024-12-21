"use client"

import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Plug} from "lucide-react";
import {useState} from "react";
import {TellerConnectEnrollment} from "teller-connect-react/src/types";
import {useRouter} from "next/navigation";
import {useStore} from "@/store.ts";

const ImportButton = () => {
  const [inProgress, setInProgress] = useState(false)

  const { currentAccount } = useStore()
  const router = useRouter()
  const { toast } = useToast()

  async function onTellerButtonClick(authorization?: TellerConnectEnrollment) {
    setInProgress(true)

    let url = "/api/import/" + currentAccount!["id"]
    if (authorization)
      url += "?access_token=" + authorization.accessToken + "&enrollment_id=" + authorization.enrollment.id
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
        <Button size="sm" className="h-8 gap-1" onClick={() => onTellerButtonClick()} disabled={inProgress}>
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