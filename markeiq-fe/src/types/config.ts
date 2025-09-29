export interface SidebarLink {
    label: string;
    href: string;
    icon?: React.ComponentType<{ className?: string }>;
    children?: SidebarLink[];
  }
  
  export interface SidebarGroup {
    label: string;
    items: SidebarLink[];
  }