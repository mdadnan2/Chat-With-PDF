import apiClient from "@/lib/api-client";
import type { ChatRequest, ChatResponse, UploadResponse } from "@/types";

export const uploadService = {
  uploadPDF: async (
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await apiClient.post<UploadResponse>(
      "/api/v1/upload/",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (e.total) {
            onProgress?.(Math.round((e.loaded * 100) / e.total));
          }
        },
      }
    );
    return data;
  },
};

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>("/chat/", request);
    return data;
  },
};
