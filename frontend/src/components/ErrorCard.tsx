import {Skeleton} from "@/components/ui/skeleton.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Separator} from "@/components/ui/separator.tsx";

export default async function ErrorCard() {
  return (
    <Card className="mb-2 overflow-hidden">
      <CardHeader className="pb-0">
        <CardTitle>Error loading Card</CardTitle>
        <CardDescription/>
      </CardHeader>
      <CardContent className="p-0">
        <Separator className="balance-separator mt-4"/>
          <div className="w-full relative">
            {[...Array(3)].map(() =>
            <div className="containers tx-row-border">
              <div className="left">
                <Skeleton className="date h-6 w-32"/>
                <Skeleton className="remoteName h-6 w-40"/>
                <Skeleton className="purpose h-6 w-48"/>
              </div>
              <div className="right">
                <Skeleton className="w-24 h-10"/>
                <Skeleton className="price text-sm h-6 w-20"/>
              </div>
            </div>
            )}
          </div>
      </CardContent>
    </Card>
  )
}