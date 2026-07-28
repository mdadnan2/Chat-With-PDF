export { useAuth } from "@/providers/auth-provider";
export { useDocument } from "@/providers/document-provider";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authService, documentService } from "@/services/api";
import type { RegisterRequest } from "@/types";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: authService.me,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: documentService.list,
    staleTime: 30 * 1000,
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
  });
}
