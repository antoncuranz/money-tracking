import {Card as InternalCard, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import React from "react";

export default async function Card({
  title,
  children,
  headerSlot
}: {
  title: string,
  children: React.ReactNode,
  headerSlot?: React.ReactNode
}) {

  return (
    <InternalCard className="mb-2 overflow-hidden card">
      <CardHeader className="pb-0 flex-row justify-between" style={{height: "3.375rem"}}>
        <CardTitle>
          {title}
        </CardTitle>
        {headerSlot}
      </CardHeader>
      <CardContent className="p-0">
        <Separator className="mt-4"/>
        {children}
      </CardContent>
    </InternalCard>
  )
}