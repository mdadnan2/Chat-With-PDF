import apiClient from "@/lib/api-client";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UploadResponse,
  ChatRequest,
  ChatResponse,
  Document,
  DeleteResponse,
} from "@/types";

export const authService = {
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const { data: res } = await apiClient.post<RegisterResponse>("/auth/register", data);
    return res;
  },

  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const params = new URLSearchParams();
    params.append("username", data.username);
    params.append("password", data.password);
    const { data: res } = await apiClient.post<LoginResponse>("/auth/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return res;
  },

  me: async (): Promise<AuthUser> => {
    const { data } = await apiClient.get<AuthUser>("/auth/me");
    return data;
  },
};

export const uploadService = {
  uploadPDF: async (
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await apiClient.post<UploadResponse>("/api/v1/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 300000,
      onUploadProgress: (e) => {
        if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total));
      },
    });
    return data;
  },
};

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>("/chat/", request);
    return data;
  },
};

export const documentService = {
  list: async (): Promise<Document[]> => {
    const { data } = await apiClient.get<{ documents: Document[] }>("/documents");
    return data.documents;
  },

  delete: async (id: string): Promise<DeleteResponse> => {
    const { data } = await apiClient.delete<DeleteResponse>(`/documents/${id}`);
    return data;
  },
};
