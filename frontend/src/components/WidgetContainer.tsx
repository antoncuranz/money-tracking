"use client"

import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";
import React from "react";
import {useResponsiveState} from "@/components/ResponsiveStateProvider.tsx";

interface Props {
  widgets: {
    title: string;
    content: React.JSX.Element,
    hideTitleDesktop?: boolean
  }[],
}

const WidgetContainer = ({widgets}: Props) => {

  const { isMobile } = useResponsiveState()
  
  return (
    <>
      {isMobile ?
        <Card className="mb-2">
          <CardContent className="pb-0">
            <Accordion type="single" collapsible className="w-full">
              {widgets.map((w, idx) =>
                <AccordionItem key={w.title} value={w.title} className={idx == widgets.length-1 ? "border-0" : ""}>
                  <AccordionTrigger>{w.title}</AccordionTrigger>
                  <AccordionContent>
                    {w.content}
                  </AccordionContent>
                </AccordionItem>
              )}
            </Accordion>
          </CardContent>
        </Card>
      :
        <>
          {widgets.map(w =>
            <Card key={w.title} className="mb-2">
              {w.hideTitleDesktop ? w.content :
                <>
                  <CardHeader>
                    <CardTitle>{w.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {w.content}
                  </CardContent>
                </>
              }
            </Card>
          )}
        </>
      }
    </>
  )
}

export default WidgetContainer