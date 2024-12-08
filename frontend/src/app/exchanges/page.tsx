import React, {Suspense} from "react";
import AddExchangeButton from "@/components/buttons/AddExchangeButton.tsx";
import ExchangesCard from "@/components/card/ExchangesCard.tsx";
import SkeletonCard from "@/components/card/SkeletonCard.tsx";
import PaymentsCard from "@/components/card/PaymentsCard.tsx";
import VirtualAccountBalanceWidget from "@/components/widgets/VirtualAccountBalanceWidget.tsx";
import ExchangeAmountWidget from "@/components/widgets/ExchangeAmountWidget.tsx";
import SkeletonWidget from "@/components/widgets/SkeletonWidget.tsx";
import {ErrorBoundary} from "react-error-boundary";

export const dynamic = 'force-dynamic'

export default async function Page() {

  return (
    <>
      <div className="flex justify-between h-10">
        <div/>
        <div className="flex items-center gap-2">
          <AddExchangeButton/>
        </div>
      </div>
      <div className="not-mobile-flex gap-2 mb-2">
        <div className="shrink-0" style={{minWidth: "18.1rem"}}>
          <Suspense fallback={<SkeletonWidget/>}>
            <ExchangeAmountWidget/>
          </Suspense>
          <Suspense fallback={<SkeletonWidget/>}>
            <VirtualAccountBalanceWidget/>
          </Suspense>
        </div>
        <div className="flex-auto min-w-0">
          <Suspense fallback={<SkeletonCard/>}>
            <ErrorBoundary fallback={<SkeletonCard title="Error loading Exchanges"/>}>
              <ExchangesCard/>
            </ErrorBoundary>
          </Suspense>
          <Suspense fallback={<SkeletonCard/>}>
            <ErrorBoundary fallback={<SkeletonCard title="Error loading Payments"/>}>
              <PaymentsCard/>
            </ErrorBoundary>
          </Suspense>
        </div>
      </div>
    </>
  )
}