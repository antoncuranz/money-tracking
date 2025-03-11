import Link from "next/link";
import {ModeToggle} from "@/components/buttons/ModeToggle.tsx";

export default function Navigation(){
  return (
    <header className="sticky top-0 flex h-16 items-center gap-4 border-b pr-4 md:pr-6 z-10 border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 dark:border-border">
      <nav className="font-medium flex flex-row items-center gap-5 text-sm lg:gap-6 w-full">
        <div className="flex gap-4 lg:gap-6 overflow-x-auto w-full no-scrollbar h-10 items-center pl-4 md:pl-6 pr-10"
             style={{maskImage: "linear-gradient(to right, transparent .0em, black 1em calc(100% - 3em), transparent calc(100% - .0em))"}}
        >
          <Link href="/">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Transactions</span>
          </Link>
          <Link href="/exchanges">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Exchanges</span>
          </Link>
          <Link href="/archive">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Archive</span>
          </Link>
          <Link href="/accounts">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Accounts</span>
          </Link>
        </div>
        <ModeToggle/>
      </nav>
    </header>
  )
}