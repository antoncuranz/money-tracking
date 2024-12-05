import type { Metadata } from 'next'
import {CreditCard, ExternalLink} from "lucide-react";
import Link from "next/link";
import '../index.css'
import {Toaster} from "@/components/ui/toaster.tsx";

export const metadata: Metadata = {
  title: "money-tracking"
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {

  return (
    <html lang="en">
    <body>
      <div className="flex min-h-screen w-full flex-col bg-muted/40">
        <header
          className="sticky top-0 flex h-16 items-center gap-4 border-b px-4 md:px-6 z-10 backdrop-blur-lg bg-white/80">
          <nav
            className="font-medium flex flex-row items-center gap-5 text-sm lg:gap-6">
            <Link href="/">
              <span className="flex items-center gap-2 text-lg font-semibold md:text-base">
                <CreditCard className="h-6 w-6"/>
              </span>
            </Link>
            <Link href="/">
              <span className="text-muted-foreground transition-colors hover:text-foreground">Transactions</span>
            </Link>
            <Link href="/exchanges">
              <span className="text-muted-foreground transition-colors hover:text-foreground">Exchanges</span>
            </Link>
            <Link href="/archive">
              <span className="text-muted-foreground transition-colors hover:text-foreground">Archive</span>
            </Link>
            <a href="https://actual.serverton.de"
               className="text-muted-foreground transition-colors hover:text-foreground">
              Actual
              <ExternalLink className="h-4 w-4 ml-1" style={{display: "inline", verticalAlign: "text-top"}}/>
            </a>
          </nav>
        </header>
        <div id="root">{children}</div>
        <Toaster/>
      </div>
    </body>
    </html>
  )
}