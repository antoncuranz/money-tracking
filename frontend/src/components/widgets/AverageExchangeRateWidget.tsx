import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {fetchBalances, hideIfUnauthorized} from "@/requests.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";


export default async function AverageExchangeRateWidget() {
  return hideIfUnauthorized(async () => {
    const balances = await fetchBalances()

    return(
      <PrivacyFilter>
        <Card className="mb-2">
          <CardHeader className="pb-0">
            <CardTitle>{balances.avg_exchange_rate.toString()}</CardTitle>
            <CardDescription>
              <span className="text-lg">average exchange rate<br/>of unpaid transactions</span>
            </CardDescription>
          </CardHeader>
          <CardContent/>
        </Card>
      </PrivacyFilter>
    )
  })
}