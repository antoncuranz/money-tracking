import React, {Suspense} from "react";
import {Skeleton} from "@/components/ui/skeleton.tsx";
import AccountSelector from "src/components/AccountSelector";
import ImportButton from "@/components/buttons/ImportButton.tsx";
import ActualButton from "@/components/buttons/ActualButton.tsx";
import TxSaveButton from "@/components/buttons/TxSaveButton.tsx";
import WidgetContainer from "@/components/widgets/WidgetContainer.tsx";
import DueDateCalendar from "@/components/widgets/DueDateCalendar.tsx";
import BalancesWidget from "@/components/widgets/BalancesWidget.tsx";
import SkeletonCard from "@/components/card/SkeletonCard.tsx";
import CreditsCard from "@/components/card/CreditsCard.tsx";
import TransactionsCard from "@/components/card/TransactionsCard.tsx";
import {ErrorBoundary} from "react-error-boundary";
import {isSuperUser} from "@/requests.ts";

export default async function Page() {

  const widgets = [
    {
      title: "Calendar",
      content: <DueDateCalendar/>,
      hideTitleDesktop: true
    },
    {
      title: "Balances",
      content: (
        <Suspense fallback={<Skeleton className="h-10"/>}>
          <BalancesWidget/>
        </Suspense>
      )
    }
  ]
  
  if (await isSuperUser()) {
    widgets.push({
      title: "Other Balances",
      content: (
        <Suspense fallback={<Skeleton className="h-10"/>}>
          <BalancesWidget showMyAccounts={false}/>
        </Suspense>
      )
    })
  }

  return (
    <>
      <div className="flex justify-between h-10">
        <AccountSelector/>
        <div className="flex items-center gap-2">
          <ImportButton/>
          <ActualButton/>
          <TxSaveButton/>
        </div>
      </div>
      <div className="not-mobile-flex gap-2 mb-2">
        <div className="shrink-0" style={{minWidth: "18.1rem"}}>
          <WidgetContainer widgets={widgets}/>
        </div>
        <div className="flex-auto min-w-0">
          <Suspense fallback={<SkeletonCard/>}>
            <ErrorBoundary fallback={<SkeletonCard title="Error loading Credits"/>}>
              <CreditsCard/>
            </ErrorBoundary>
          </Suspense>
          <Suspense fallback={<SkeletonCard/>}>
            <ErrorBoundary fallback={<SkeletonCard title="Error loading Transactions"/>}>
              <TransactionsCard/>
            </ErrorBoundary>
          </Suspense>
        </div>
      </div>
    </>
  )
}