export interface UploadMetadata {
  id: string;
  original_name: string;
  stored_name: string;
  content_type: string;
  extension: string;
  size: number;
  uploaded_at: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  data: UploadMetadata;
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
}

export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

export interface DocumentInfo {
  id: string;
  name: string;
  size: number;
  pages?: number;
  uploadedAt: string;
}
