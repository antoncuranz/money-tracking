import type {Metadata, Viewport} from 'next'
import '../index.css'
import {Toaster} from "@/components/ui/toaster.tsx";
import {ThemeProvider} from "@/components/provider/ThemeProvider.tsx";
import Navigation from "@/components/navigation/Navigation.tsx";

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
        <Navigation/>
        <div id="root" className="flex min-h-screen w-full flex-col bg-muted/40">
          <div className="flex flex-col sm:gap-4 sm:py-4">
            <main className="grid flex-1 items-start gap-2 p-4 sm:px-6 sm:py-0 md:gap-2">
              {children}
            </main>
          </div>
        </div>
        <Toaster/>
      </ThemeProvider>
    </body>
    </html>
  )
}