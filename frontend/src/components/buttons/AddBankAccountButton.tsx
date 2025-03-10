"use client"

import {Button} from "@/components/ui/button.tsx";
import {Landmark} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import BankAccountDialog from "@/components/dialog/BankAccountDialog.tsx";
import {PlaidConnection} from "@/types.ts";

export default function AddBankAccountButton({connections}: {connections: PlaidConnection[]}) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const router = useRouter()

  function onDialogClose(needsUpdate: boolean) {
    setDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  return (
    <>
      <Button size="sm" className="h-8 gap-1 mt-0 self-end" onClick={() => setDialogOpen(true)}>
        <Landmark className="h-3.5 w-3.5"/>
        <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
          Add Bank Account
        </span>
      </Button>
      <BankAccountDialog open={dialogOpen} onClose={onDialogClose} connections={connections}/>
    </>
  )
}