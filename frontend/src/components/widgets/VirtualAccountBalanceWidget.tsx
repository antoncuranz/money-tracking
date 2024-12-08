import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {formatAmount} from "@/components/util.ts";
import {fetchBalances} from "@/requests.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";

export default async function VirtualAccountBalanceWidget() {
  const balances = await fetchBalances()

  return (
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
}