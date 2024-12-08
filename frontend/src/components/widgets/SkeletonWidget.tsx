import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Skeleton} from "@/components/ui/skeleton.tsx";

export default async function SkeletonWidget() {

  return (
    <Card className="mb-2">
      <CardHeader className="pb-0">
        <CardTitle>
          <Skeleton className="h-8 w-40"/>
        </CardTitle>
      </CardHeader>
      <CardContent/>
    </Card>
  )
}