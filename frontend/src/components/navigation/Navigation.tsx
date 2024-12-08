import Link from "next/link";
import {ModeToggle} from "@/components/navigation/ModeToggle.tsx";

export default function Navigation(){
  return (
    <header className="sticky top-0 flex h-16 items-center gap-4 border-b px-4 md:px-6 z-10 border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 dark:border-border">
      <nav className="font-medium flex flex-row items-center gap-5 text-sm lg:gap-6 w-full">
        <Link href="/">
          <span className="text-muted-foreground transition-colors hover:text-foreground">Transactions</span>
        </Link>
        <Link href="/exchanges">
          <span className="text-muted-foreground transition-colors hover:text-foreground">Exchanges</span>
        </Link>
        <Link href="/archive">
          <span className="text-muted-foreground transition-colors hover:text-foreground">Archive</span>
        </Link>
        <div className="flex-grow"/>
        <ModeToggle/>
      </nav>
    </header>
  )
}