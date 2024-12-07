import SkeletonCard from "@/components/SkeletonCard.tsx";
import {Skeleton} from "@/components/ui/skeleton.tsx";
import SkeletonWidgetContainer from "@/components/SkeletonWidgetContainer.tsx";

export default async function Loading() {

  return (
    <>
      <div className="flex justify-between h-10">
        <Skeleton className="h-10 w-40"/>
      </div>
      <div className="not-mobile-flex gap-2 mb-2">
        <div className="flex-initial">
          <SkeletonWidgetContainer/>
        </div>
        <div className="flex-auto min-w-0">
          <SkeletonCard/>
          <SkeletonCard/>
        </div>
      </div>
    </>
  )
}