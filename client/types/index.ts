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

export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  sources?: string[];
}

export interface DocumentInfo {
  id: string;
  name: string;
  size: number;
  pages?: number;
  uploadedAt: string;
}

// Auth types
export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface RegisterRequest {
  name?: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
  name?: string;
  full_name?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Document types (backend shape)
export interface Document {
  id: string;
  original_filename: string;
  stored_filename: string;
  uploaded_at: string;
}

// Chat types
export interface ChatRequest {
  document_id: string;
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export interface DeleteResponse {
  success: boolean;
  message: string;
}
