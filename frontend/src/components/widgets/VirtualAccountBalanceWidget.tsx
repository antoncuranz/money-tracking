import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import {fetchBalances, hideIfUnauthorized} from "@/requests.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import React from "react";


export default async function VirtualAccountBalanceWidget() {
  return hideIfUnauthorized(async () => {
    const balances = await fetchBalances()

    return(
      <PrivacyFilter>
        <Card className="mb-2">
          <CardHeader className="pb-0">
            <CardTitle>{formatAmount(balances.virtual_account)}</CardTitle>
            <CardDescription>
              <span className="text-lg">virtual account balance</span>
            </CardDescription>
          </CardHeader>
          <CardContent/>
        </Card>
      </PrivacyFilter>
    )
  })
}