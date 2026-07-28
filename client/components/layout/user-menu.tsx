"use client";

import { useRouter } from "next/navigation";
import { LogOut, User } from "lucide-react";
import { toast } from "sonner";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/providers/auth-provider";
import { useDocument } from "@/providers/document-provider";

export function UserMenu() {
  const { user, logout } = useAuth();
  const { setDocument } = useDocument();
  const router = useRouter();

  if (!user) return null;

  const displayName = user.full_name ?? user.email.split("@")[0];

  const handleLogout = () => {
    logout();
    setDocument(null);
    toast.success("Signed out successfully");
    router.replace("/login");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex items-center gap-2 rounded-lg p-1 hover:bg-accent transition-colors outline-none">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="text-[11px]">{displayName.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <span className="hidden sm:block text-sm font-medium max-w-[120px] truncate">
            {displayName}
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            {user.full_name && (
              <p className="text-sm font-medium leading-none">{user.full_name}</p>
            )}
            <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <User className="h-4 w-4" />
          Profile
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={handleLogout}
          className="text-destructive focus:text-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
