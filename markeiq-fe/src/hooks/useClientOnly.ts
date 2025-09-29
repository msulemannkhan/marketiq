import { useEffect, useState } from 'react';

/**
 * Hook to prevent hydration mismatch by only rendering content on the client side
 * @returns boolean indicating if the component is mounted on the client
 */
export function useClientOnly(): boolean {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return mounted;
}
