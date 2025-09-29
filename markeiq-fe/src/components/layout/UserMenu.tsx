"use client";

import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem, User, Spinner, Skeleton } from "@heroui/react";
import { useAppDispatch, useAppSelector } from "@/lib/redux/hooks";
import { logoutUser, getCurrentUser } from "@/lib/redux/slices/authSlice";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useClientOnly } from "@/hooks/useClientOnly";
import { cn } from "@/lib/utils";

export default function UserMenu() {
  const dispatch = useAppDispatch();
  const router = useRouter();
  // `isLoading` from Redux state is used to determine if user data is being fetched.
  // Renamed to `authLoading` for clarity to avoid conflict if a local `isLoading` were added.
  const { user, isAuthenticated, isLoading: authLoading } = useAppSelector((state) => state.auth);
  const { isCollapsed } = useAppSelector((state) => state.sidebar);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const mounted = useClientOnly();

  // Fetch fresh user data on mount to ensure UserMenu shows current data
  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, isAuthenticated, user]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      // Dispatch the logoutUser thunk.
      await dispatch(logoutUser());
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleProfileClick = () => {
    router.push('/dashboard/profile');
  };

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className={cn("flex items-center gap-4", isCollapsed && "justify-center")}>
        {/* Skeleton for the avatar */}
        <Skeleton className="flex rounded-full w-10 h-10" />
        {!isCollapsed && (
          <div className="flex flex-col gap-2">
            {/* Skeleton for the user's name */}
            <Skeleton className="h-3 w-24 rounded-lg" />
            {/* Skeleton for the username/description */}
            <Skeleton className="h-3 w-20 rounded-lg" />
          </div>
        )}
      </div>
    );
  }

  // Show a skeleton while the authentication state or user data is being loaded.
  // This covers the period when `getCurrentUser` (or similar logic within the auth slice)
  // is fetching the user's information.
  if (authLoading) {
    return (
      <div className={cn("flex items-center gap-4", isCollapsed && "justify-center")}>
        {/* Skeleton for the avatar */}
        <Skeleton className="flex rounded-full w-10 h-10" />
        {!isCollapsed && (
          <div className="flex flex-col gap-2">
            {/* Skeleton for the user's name */}
            <Skeleton className="h-3 w-24 rounded-lg" />
            {/* Skeleton for the username/description */}
            <Skeleton className="h-3 w-20 rounded-lg" />
          </div>
        )}
      </div>
    );
  }

  // If not authenticated or user data is missing after loading, do not render the menu.
  if (!isAuthenticated || !user) {
    return null;
  }

  // Generate avatar URL, falling back to a generic UI-avatars image if `avatar_url` is not available
  // or if `full_name` is missing (though `!user` check should prevent this).
  const avatarUrl = user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || 'User')}&background=random`;

  return (
    <div className={cn("flex items-center gap-4", isCollapsed && "justify-center")}>
      <Dropdown placement="bottom-start">
        <DropdownTrigger as="button">
          <User
            as="button"
            avatarProps={{
              isBordered: true,
              src: avatarUrl,
            }}
            className="transition-transform cursor-pointer "
            description={!isCollapsed ? `@${user?.username}` : undefined}
            name={!isCollapsed ? user?.full_name : undefined}
            classNames={{
              name: "truncate", // Added for line-clamping the name
            }}
          />
        </DropdownTrigger>
        <DropdownMenu aria-label="User Actions" variant="flat">
          <DropdownItem key="profile" className="h-14 gap-2" onClick={handleProfileClick}>
            <User
              avatarProps={{
                size: "sm",
                src: avatarUrl,
              }}
              classNames={{
                name: "text-default-600 truncate",
                description: "text-default-500",
              }}
              description={`@${user?.username}`}
              name={user?.full_name}
            />
          </DropdownItem>
          <DropdownItem key="settings" onClick={handleProfileClick}>
            My Settings
          </DropdownItem>
          <DropdownItem key="analytics" onClick={() => router.push('/dashboard/analytics')}>
            Analytics
          </DropdownItem>
          <DropdownItem key="catalog" onClick={() => router.push('/dashboard/catalog')}>
            Catalog
          </DropdownItem>
          <DropdownItem key="chat" onClick={() => router.push('/dashboard/chat')}>
            Chat
          </DropdownItem>
          <DropdownItem key="help_and_feedback">
            Help & Feedback
          </DropdownItem>
          <DropdownItem
            key="logout"
            color="danger"
            onClick={handleLogout}
            isDisabled={isLoggingOut}
            className="flex items-center gap-2"
          >
            {isLoggingOut ? (
              <>
                <Spinner size="sm" color="danger" />
                Logging out...
              </>
            ) : (
              'Log Out'
            )}
          </DropdownItem>
        </DropdownMenu>
      </Dropdown>
    </div>
  );
}
