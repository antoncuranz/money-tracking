import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import {fetchFees, hideIfUnauthorized} from "@/requests.ts";

export default async function FxFeesWidget() {
  return hideIfUnauthorized(async () => {
    const fees = await fetchFees()

    return (
      <Card className="mb-2">
        <CardHeader className="pb-0">
          <CardTitle>{formatAmount(fees?.fees_and_risk_eur ?? 0)}</CardTitle>
          <CardDescription>
            TOTAL FX FEES AND CCY RISK
          </CardDescription>
        </CardHeader>
        <CardContent/>
      </Card>
    )
  })
}