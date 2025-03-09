import {fetchBalances, hideIfUnauthorized} from "@/requests.ts";
import React from "react";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";

export default async function ExchangeAmountWidget() {
  return hideIfUnauthorized(async () => {
    const balances = await fetchBalances()
    
    return (
      <PrivacyFilter>
        <Card className="mb-2">
          <CardHeader className="pb-0">
            <CardTitle>{formatAmount(balances.total)}</CardTitle>
            <CardDescription>
            <span
              className="text-lg">{formatAmount(balances.posted)} + {formatAmount(balances.pending)}</span> pending
              <br/>
              <span className="text-lg"> - {formatAmount(balances.credits)}</span> credits
              <br/>
              <span className="text-lg"> - {formatAmount(balances.exchanged)}</span> exchanged
            </CardDescription>
          </CardHeader>
          <CardContent/>
        </Card>
      </PrivacyFilter>
    )
  })
}