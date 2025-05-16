"use client"

import React from "react";
import {useStore} from "@/store.ts";
import {Switch} from "@/components/ui/switch.tsx";
import {Label} from "@radix-ui/react-label";
import {Filter} from "lucide-react";

export const MissingAmountEurFilter = () => {
  const { filterMissingAmountEur, setFilterMissingAmountEur } = useStore()

  return (
    <div className="flex items-center space-x-2 h-8" style={{margin: 0}}>
      <Filter className="h-5 w-5 sm:sr-only"/>
      <Label htmlFor="missing-amount-eur-filter" className="text-sm sr-only sm:not-sr-only">Missing EUR amounts</Label>
      <Switch id="missing-amount-eur-filter"
              checked={filterMissingAmountEur}
              onCheckedChange={setFilterMissingAmountEur}
      />
    </div>
  )
}
