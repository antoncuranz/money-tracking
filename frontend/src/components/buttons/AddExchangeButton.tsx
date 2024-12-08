"use client"

import {Button} from "@/components/ui/button.tsx";
import {Coins} from "lucide-react";
import {useState} from "react";
import {useRouter} from "next/navigation";
import ExchangeDialog from "@/components/dialog/ExchangeDialog.tsx";

export default function AddExchangeButton () {
  const [exchangeDialogOpen, setExchangeDialogOpen] = useState(false)
  const router = useRouter()

  function onExchangeDialogClose(needsUpdate: boolean) {
    setExchangeDialogOpen(false)

    if (needsUpdate)
      router.refresh()
  }

  return (
    <>
      <Button size="sm" className="h-8 gap-1" onClick={() => setExchangeDialogOpen(true)}>
        <Coins className="h-3.5 w-3.5"/>
        <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
          Add Exchange
        </span>
      </Button>
      <ExchangeDialog open={exchangeDialogOpen} onClose={onExchangeDialogClose}/>
    </>
  )
}