"use client"

import {Exchange} from "@/types.ts";
import ExchangeRow from "@/components/table/ExchangeRow.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {useRouter} from "next/navigation";
import {useStore} from "@/store.ts";

export default function ExchangeTable({
  exchanges
}: {
  exchanges: Exchange[]
}) {
  const { exchangeSelection, setExchangeSelection } = useStore()
  const { toast } = useToast();
  const router = useRouter();

  async function deleteExchange(exId: number) {
    const url = "/api/exchanges/" + exId
    const response = await fetch(url, {method: "DELETE"})

    if (response.ok)
      router.refresh()
    else toast({
      title: "Error deleting Exchange",
      description: response.statusText
    })
  }

  return (
    <div className="w-full relative card-table">
      {exchanges.map(exchange =>
        <ExchangeRow key={exchange["id"]} exchange={exchange} selected={exchangeSelection == exchange["id"]}
                     disabled={exchangeSelection != null}
                     selectExchange={() => setExchangeSelection(exchange["id"])}
                     deleteExchange={() => deleteExchange(exchange["id"])}
                     unselectExchange={() => setExchangeSelection(null)}/>
      )}
    </div>
  )
}