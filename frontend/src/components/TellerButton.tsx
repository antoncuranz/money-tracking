import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {Plug} from "lucide-react";
import {useTellerConnect} from "teller-connect-react";

interface Props {
  account: any,
  updateData?: () => void,
}

const TellerButton = ({account, updateData=() => {}}: Props) => {
  const { toast } = useToast();

  const { open: openTeller, ready: isTellerReady } = useTellerConnect({
    applicationId: import.meta.env.VITE_TELLER_APPLICATION_ID,
    environment: "sandbox",
    enrollmentId: account["teller_enrollment_id"],
    onSuccess: authorization => {
      toast({
        title: "Teller success",
        description: authorization.accessToken
      })
      onTellerButtonClick(authorization.accessToken)
    },
    onFailure: failure => toast({
      title: "Teller failure",
      description: failure.message
    })
  });

  async function onTellerButtonClick(accessToken?: string) {
    let url = "/api/import/" + account["id"]
    if (accessToken)
      url += "?access_token=" + accessToken
    const response = await fetch(url, {method: "POST"})

    if (!accessToken && response.status == 418) // if mfa required: authorize and try again!
      openTeller()

    if (updateData)
      updateData()
  }

  return (
    <Button size="sm" className="h-8 gap-1" onClick={() => onTellerButtonClick()} disabled={!account || !isTellerReady}>
      <Plug className="h-3.5 w-3.5"/>
      <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
        Teller Connect
      </span>
    </Button>
  )
}

export default TellerButton