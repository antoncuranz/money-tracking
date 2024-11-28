import './App.css'
import {Toaster} from "@/components/ui/toaster.tsx";
import {ExternalLink, CreditCard} from 'lucide-react';

import {NavLink, Route, Routes} from "react-router-dom";
import TransactionPage from "@/TransactionPage.tsx";
import ExchangePage from "@/ExchangePage.tsx";
import ArchivePage from "@/ArchivePage.tsx";

const App = () => {

  return (<>
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      <header className="sticky top-0 flex h-16 items-center gap-4 border-b px-4 md:px-6 z-10 backdrop-blur-lg bg-white/80">
        <nav
          className="font-medium flex flex-row items-center gap-5 text-sm lg:gap-6">
          <NavLink to="/">
            <span className="flex items-center gap-2 text-lg font-semibold md:text-base">
              <CreditCard className="h-6 w-6"/>
            </span>
          </NavLink>
          <NavLink to="/">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Transactions</span>
          </NavLink>
          <NavLink to="/exchanges">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Exchanges</span>
          </NavLink>
          <NavLink to="/archive">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Archive</span>
          </NavLink>
          <a href="https://actual.serverton.de"
             className="text-muted-foreground transition-colors hover:text-foreground">
            Actual
            <ExternalLink className="h-4 w-4 ml-1" style={{display: "inline", verticalAlign: "text-top"}}/>
          </a>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<TransactionPage/>}/>
        <Route path="/transactions" element={<TransactionPage/>}/>
        <Route path="/exchanges" element={<ExchangePage/>}/>
        <Route path="/archive" element={<ArchivePage/>}/>
      </Routes>
      <Toaster/>
    </div>
  </>
)
}

export default App