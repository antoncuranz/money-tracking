import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {LoaderCircle, Plug} from "lucide-react";
import {useTellerConnect} from "teller-connect-react";
import {useState} from "react";
import {TellerConnectEnrollment} from "teller-connect-react/src/types";

interface Props {
  account: Account,
  updateData?: () => void,
}

const TellerButton = ({account, updateData=() => {}}: Props) => {
  const [inProgress, setInProgress] = useState(false)
  const { toast } = useToast();

  const { open: openTeller, ready: isTellerReady } = useTellerConnect({
    applicationId: import.meta.env.VITE_TELLER_APPLICATION_ID,
    environment: "development",
    enrollmentId: account.teller_enrollment_id ?? "",
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

    let url = "/api/import/" + account["id"]
    if (authorization)
      url += "?access_token=" + authorization.accessToken + "&enrollment_id=" + authorization.enrollment.id + "&teller_id=" + authorization.user.id
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

    if (updateData)
      updateData()

    setInProgress(false)
  }

  return (
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
  )
}

export default TellerButton