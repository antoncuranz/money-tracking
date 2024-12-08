import React, {Suspense} from "react";
import SkeletonCard from "@/components/card/SkeletonCard.tsx";
import ArchiveCard from "@/components/card/ArchiveCard.tsx";
import FxFeesWidget from "@/components/widgets/FxFeesWidget.tsx";
import SkeletonWidget from "@/components/widgets/SkeletonWidget.tsx";
import {ErrorBoundary} from "react-error-boundary";

export const dynamic = 'force-dynamic'

export default async function Page() {

  return (
    <div className="not-mobile-flex gap-2 mb-2">
      <div className="shrink-0" style={{minWidth: "18.1rem"}}>
        <Suspense fallback={<SkeletonWidget/>}>
          <FxFeesWidget/>
        </Suspense>
      </div>
      <div className="flex-auto min-w-0">
        <Suspense fallback={<SkeletonCard/>}>
          <ErrorBoundary fallback={<SkeletonCard title="Error"/>}>
            <ArchiveCard/>
          </ErrorBoundary>
        </Suspense>
      </div>
    </div>
  )
}