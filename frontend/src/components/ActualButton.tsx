import {useToast} from "@/components/ui/use-toast.ts";
import {Button} from "@/components/ui/button.tsx";
import {Import, LoaderCircle} from "lucide-react";
import {useState} from "react";
import {Account} from "@/types.ts";

interface Props {
  account: Account,
  updateData?: () => void,
}

const ActualButton = ({account, updateData=() => {}}: Props) => {
  const [inProgress, setInProgress] = useState(false)
  const { toast } = useToast();

  async function onClick() {
    setInProgress(true)

    const response = await fetch("/api/actual/" + account.id, {method: "POST"})

    if (!response.ok) {
      toast({
        title: "Error during Actual import",
        description: response.statusText
      })
    }

    if (updateData)
      updateData()

    setInProgress(false)
  }

  return (
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
  )
}

export default ActualButton