import {Card as InternalCard, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import React from "react";

export default async function Card({
  title,
  children
}: {
  title: string,
  children: React.ReactNode
}) {

  return (
    <InternalCard className="mb-2 overflow-hidden">
      <CardHeader className="pb-0">
        <CardTitle>{title}</CardTitle>
        <CardDescription/>
      </CardHeader>
      <CardContent className="p-0">
        <Separator className="mt-4"/>
        {children}
      </CardContent>
    </InternalCard>
  )
}