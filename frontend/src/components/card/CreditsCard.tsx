import {Account, Credit} from "@/types.ts";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import CreditTable from "@/components/table/CreditTable.tsx";

export default async function CreditsCard() {
  const accountResponse = await fetch(process.env.BACKEND_URL + "/api/accounts", {cache: "no-cache"})
  const accounts = await accountResponse.json() as Account[]

  const creditResponse = await fetch(process.env.BACKEND_URL + "/api/credits?usable=true", {cache: "no-cache"})
  const credits = await creditResponse.json() as Credit[]

  return (
    <>
      {credits.length > 0 &&
        <Card className="mb-2 overflow-hidden">
          <CardHeader className="pb-0">
            <CardTitle>Credits</CardTitle>
            <CardDescription/>
          </CardHeader>
          <CardContent className="p-0">
            <Separator className="balance-separator mt-4"/>
            <CreditTable credits={credits} accounts={accounts}/>
          </CardContent>
        </Card>
      }
    </>
  )
}