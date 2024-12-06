import type {Metadata, Viewport} from 'next'
import '../index.css'
import {Toaster} from "@/components/ui/toaster.tsx";
import Navigation from "@/components/Navigation.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export const metadata: Metadata = {
  title: "money-tracking",
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1.0,
  maximumScale: 1.0
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {

  return (
    <html lang="en" suppressHydrationWarning>
    <body>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <div id="root" className="flex min-h-screen w-full flex-col bg-muted/40">
          <Navigation/>
          {children}
        </div>
        <Toaster/>
      </ThemeProvider>
    </body>
    </html>
  )
}