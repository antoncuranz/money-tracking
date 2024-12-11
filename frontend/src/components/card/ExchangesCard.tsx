import {fetchExchanges} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import ExchangeTable from "@/components/table/ExchangeTable.tsx";
import {Exchange} from "@/types.ts";
import AddExchangeButton from "@/components/buttons/AddExchangeButton.tsx";
import React from "react";

export default async function ExchangesCard() {
  let exchanges: Exchange[] = []
  try {
    exchanges = await fetchExchanges()
  } catch (e) { /* probably unauthorized */ }

  return (
    <>
      {exchanges.length > 0 &&
        <Card title="Exchanges" headerSlot={<AddExchangeButton/>}>
            <ExchangeTable exchanges={exchanges}/>
        </Card>
      }
    </>
  )
}