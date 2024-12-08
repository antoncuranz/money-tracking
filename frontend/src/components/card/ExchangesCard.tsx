import {fetchExchanges} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import ExchangeTable from "@/components/table/ExchangeTable.tsx";

export default async function ExchangesCard() {
  const exchanges = await fetchExchanges()

  return (
    <>
      {exchanges.length > 0 &&
        <Card title="Exchanges">
            <ExchangeTable exchanges={exchanges}/>
        </Card>
      }
    </>
  )
}