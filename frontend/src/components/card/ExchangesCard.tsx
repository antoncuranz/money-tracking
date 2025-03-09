import {fetchExchanges, hideIfUnauthorized} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import ExchangeTable from "@/components/table/ExchangeTable.tsx";
import AddExchangeButton from "@/components/buttons/AddExchangeButton.tsx";
import React from "react";

export default async function ExchangesCard() {
  return hideIfUnauthorized(async () => {
    const exchanges = await fetchExchanges()

    return (
      <Card title="Exchanges" headerSlot={<AddExchangeButton/>}>
        <ExchangeTable exchanges={exchanges}/>
      </Card>
    )
  })
}