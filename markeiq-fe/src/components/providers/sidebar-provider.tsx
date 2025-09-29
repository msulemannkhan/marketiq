import { SidebarProvider } from "@/components/ui/sidebar"

export function AsideProvider({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
        {children}
    </SidebarProvider>
  )
}