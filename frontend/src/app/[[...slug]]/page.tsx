import {Account} from "@/types.ts";
import AccountSelector from "@/components/AccountSelector.tsx";
import WidgetContainer from "@/components/WidgetContainer.tsx";
import DueDateCalendar from "@/components/DueDateCalendar.tsx";
import TransactionsCard from "@/components/TransactionsCard.tsx";
import React, {Suspense} from "react";
import CreditsCard from "@/components/CreditsCard.tsx";
import SkeletonCard from "@/components/SkeletonCard.tsx";
import BalancesWidget from "@/components/BalancesWidget.tsx";
import ActualButton from "@/components/ActualButton.tsx";
import TellerButton from "@/components/TellerButton.tsx";
import TxSaveButton from "@/components/TxSaveButton.tsx";
import {TransactionAmountStateProvider} from "@/components/TransactionAmountStateProvider.tsx";
import {SelectionStateProvider} from "@/components/SelectionStateProvider.tsx";
import {ErrorBoundary} from "react-error-boundary";
import ErrorCard from "@/components/ErrorCard.tsx";

export default async function Page() {
  const accountResponse = await fetch(process.env.BACKEND_URL + "/api/accounts") // TODO: caching!
  const accounts = await accountResponse.json() as Account[]

  return (
    <SelectionStateProvider accounts={accounts}>
      <TransactionAmountStateProvider>
        <div className="flex flex-col sm:gap-4 sm:py-4">
          <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
            <div className="flex justify-between h-10">
              <AccountSelector accounts={accounts}/>
              <div className="flex items-center gap-2">
                <TellerButton/>
                <ActualButton/>
                <TxSaveButton/>
              </div>
            </div>
            <div className="not-mobile-flex gap-2 mb-2">
              <div className="flex-initial">
                <WidgetContainer widgets={[
                  {
                    title: "Calendar",
                    content: <DueDateCalendar/>,
                    hideTitleDesktop: true
                  },
                  {
                    title: "Balances",
                    content: <BalancesWidget accounts={accounts}/>
                  }
                ]}/>
              </div>
              <div className="flex-auto min-w-0">
                <ErrorBoundary fallback={<ErrorCard/>}>
                  <Suspense fallback={<SkeletonCard/>}>
                    <CreditsCard accounts={accounts}/>
                  </Suspense>
                </ErrorBoundary>
                <ErrorBoundary fallback={<ErrorCard/>}>
                  <Suspense fallback={<SkeletonCard/>}>
                    <TransactionsCard accounts={accounts}/>
                  </Suspense>
                </ErrorBoundary>
              </div>
            </div>
          </main>
        </div>
      </TransactionAmountStateProvider>
    </SelectionStateProvider>
  )
}