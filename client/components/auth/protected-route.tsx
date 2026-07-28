"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";

interface ProtectedRouteProps {
  children: React.ReactNode;
  /** If true, redirects authenticated users away (for login/register pages) */
  guestOnly?: boolean;
}

export function ProtectedRoute({ children, guestOnly = false }: ProtectedRouteProps) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (guestOnly && isAuthenticated) {
      router.replace("/upload");
    } else if (!guestOnly && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, loading, guestOnly, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="h-8 w-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  if (guestOnly && isAuthenticated) return null;
  if (!guestOnly && !isAuthenticated) return null;

  return <>{children}</>;
}
