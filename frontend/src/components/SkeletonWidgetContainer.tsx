"use client"

import {Card, CardContent, CardHeader} from "@/components/ui/card.tsx";
import React from "react";
import {useResponsiveState} from "@/components/ResponsiveStateProvider.tsx";
import {Skeleton} from "@/components/ui/skeleton.tsx";
import {Accordion, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";

const SkeletonWidgetContainer = () => {

  const { isMobile } = useResponsiveState()

  return isMobile ?
    <Card className="mb-2">
      <CardContent className="pb-0">
        <Accordion type="single" collapsible className="w-full">
          {[0,1].map(key =>
            <AccordionItem key={key} value={key.toString()} className={key == 1 ? "border-0" : ""}>
              <AccordionTrigger>
                <Skeleton className="h-6 w-48"/>
              </AccordionTrigger>
            </AccordionItem>
          )}
        </Accordion>
      </CardContent>
    </Card>
    :
    [0,1].map(key =>
      <Card key={key} className="mb-2">
        <CardHeader>
          <Skeleton className="h-6 w-48"/>
        </CardHeader>
        <CardContent className="p-0">
        </CardContent>
      </Card>
    )
}

export default SkeletonWidgetContainer