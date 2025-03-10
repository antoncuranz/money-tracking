import React, {Suspense} from "react";
import SkeletonCard from "@/components/card/SkeletonCard.tsx";
import {ErrorBoundary} from "react-error-boundary";
import ConnectionsCard from "@/components/card/ConnectionsCard.tsx";
import BankAccountsCard from "@/components/card/BankAccountsCard.tsx";
import CreditCardsCard from "@/components/card/CreditCardsCard.tsx";

export const dynamic = 'force-dynamic'

export default async function Page() {

  return (
    <div className="not-mobile-flex gap-2 mb-2">
      <div className="shrink-0" style={{minWidth: "18.1rem"}}>
      </div>
      <div className="flex-auto min-w-0">
        <Suspense fallback={<SkeletonCard/>}>
          <ErrorBoundary fallback={<SkeletonCard title="Error"/>}>
            <CreditCardsCard/>
          </ErrorBoundary>
        </Suspense>
        <Suspense fallback={<SkeletonCard/>}>
          <ErrorBoundary fallback={<SkeletonCard title="Error"/>}>
            <BankAccountsCard/>
          </ErrorBoundary>
        </Suspense>
        <Suspense fallback={<SkeletonCard/>}>
          <ErrorBoundary fallback={<SkeletonCard title="Error"/>}>
            <ConnectionsCard/>
          </ErrorBoundary>
        </Suspense>
      </div>
    </div>
  )
}