import './App.css'
import {Toaster} from "@/components/ui/toaster.tsx";
import {ExternalLink, CreditCard} from 'lucide-react';

import {NavLink, Route, Routes} from "react-router-dom";
import ImportPage from "@/ImportPage.tsx";
import ExchangePage from "@/ExchangePage.tsx";

const App = () => {

  return (<>
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      <header className="sticky top-0 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
        <nav
          className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
          <NavLink to="/">
            <span className="flex items-center gap-2 text-lg font-semibold md:text-base">
              <CreditCard className="h-6 w-6"/>
            </span>
          </NavLink>
          <NavLink to="/">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Overview</span>
          </NavLink>
          <NavLink to="/exchange">
            <span className="text-muted-foreground transition-colors hover:text-foreground">Exchange</span>
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
        <Route path="/" element={<ImportPage/>}/>
        <Route path="/exchange" element={<ExchangePage/>}/>
      </Routes>
      <Toaster/>
    </div>
  </>
)
}

export default App