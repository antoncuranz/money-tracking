import './App.css'
import {Button} from "@/components/ui/button.tsx";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Tabs, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {Plug, Import, Save, AlertCircle, Coins, Calculator, DraftingCompass} from 'lucide-react';

import {useToast} from "@/components/ui/use-toast.ts";
import {useEffect, useState} from "react";
import TransactionTable from "@/components/TransactionTable.tsx";
import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert.tsx";

const ExchangePage = () => {

  const { toast } = useToast();

  return (<>
      <div className="flex flex-col sm:gap-4 sm:py-4">
        <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
          <div className="flex items-center">
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="ml-auto flex items-center gap-2">
              <Button size="sm" className="h-8 gap-1">
                <Coins className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Add Exchange
                </span>
              </Button>
              <Button size="sm" className="h-8 gap-1">
                <DraftingCompass className="h-3.5 w-3.5"/>
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                  Calculate Fees
                </span>
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Card>
              <CardHeader className="pb-0">
                <CardTitle>150,00</CardTitle>
                <CardDescription>
                  <span className="text-lg">1000,00 + 50,00</span> pending <span
                  className="text-lg">- 900,00</span> exchanged
                </CardDescription>
              </CardHeader>
              <CardContent/>
            </Card>
            <Card>
              <CardHeader className="pb-0">
                {/*<CardTitle>150,00</CardTitle>*/}
                {/*<CardDescription>*/}
                {/*  <span className="text-lg">1000,00 + 50,00</span> pending <span className="text-lg">- 900,00</span> exchanged*/}
                {/*</CardDescription>*/}
              </CardHeader>
              <CardContent>
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>2 Deposits are not assigned to Exchanges</AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
          <Card>
            <CardHeader className="pb-0">
              <CardTitle>Exchanges</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-0">
              <CardTitle>Deposits</CardTitle>
              <CardDescription/>
            </CardHeader>
            <CardContent>
            </CardContent>
          </Card>
        </main>
      </div>
  </>
)
}

export default ExchangePage