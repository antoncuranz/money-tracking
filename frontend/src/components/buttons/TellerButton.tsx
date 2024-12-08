"use client"

import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Plug} from "lucide-react";
import {useTellerConnect} from "teller-connect-react";
import {useState} from "react";
import {TellerConnectEnrollment} from "teller-connect-react/src/types";
import {useRouter} from "next/navigation";
import {useSelectionState} from "@/components/provider/SelectionStateProvider.tsx";

const TellerButton = () => {
  const [inProgress, setInProgress] = useState(false)

  const { currentAccount } = useSelectionState()
  const router = useRouter()
  const { toast } = useToast()

  const { open: openTeller, ready: isTellerReady } = useTellerConnect({
    applicationId: process.env.NEXT_PUBLIC_TELLER_APPLICATION_ID!,
    environment: "development",
    enrollmentId: currentAccount?.teller_enrollment_id ?? "",
    selectAccount: "single",
    onSuccess: authorization => {
      console.log(authorization)
      onTellerButtonClick(authorization)
    },
    onFailure: failure => toast({
      title: "Teller failure",
      description: failure.message
    })
  });

  async function onTellerButtonClick(authorization?: TellerConnectEnrollment) {
    setInProgress(true)

    let url = "/api/import/" + currentAccount!["id"]
    if (authorization)
      url += "?access_token=" + authorization.accessToken + "&enrollment_id=" + authorization.enrollment.id
    const response = await fetch(url, {method: "POST"})

    if (!authorization && response.status == 418) { // if mfa required: authorize and try again!
      openTeller()
      return
    }

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
        <Button size="sm" className="h-8 gap-1" onClick={() => onTellerButtonClick()} disabled={inProgress || !isTellerReady}>
          { inProgress ?
            <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
          :
            <Plug className="h-3.5 w-3.5"/>
          }
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
          Teller Connect
          </span>
        </Button>
      }
    </>
  )
}

export default TellerButton