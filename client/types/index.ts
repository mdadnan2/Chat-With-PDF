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

export interface ChatSource {
  chunk_id: number;
  heading: string;
  similarity: number;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  sources?: ChatSource[];
}

export interface DocumentInfo {
  id: string;
  name: string;
  size: number;
  pages?: number;
  uploadedAt: string;
}

export type AgentType = "research" | "summary" | "analyst" | "document" | "verification";

export interface AgentSource {
  chunk_id: number;
  heading: string;
  similarity: number;
}

export interface AgentVerification {
  verified: boolean;
  confidence: string;
  status?: "SUPPORTED" | "UNSUPPORTED" | "INSUFFICIENT_EVIDENCE";
  explanation?: string;
  supported_claims: string[];
  unsupported_claims: string[];
  missing_evidence: string[];
  sources: AgentSource[];
}

export interface AgentRequest {
  agent: AgentType;
  document_id: string;
  question: string;
  mode?: string;
}

export interface AgentResponse {
  agent: AgentType;
  status: string;
  answer: string;
  summary?: string;
  findings?: string[];
  activity?: string[];
  sources: AgentSource[];
  verification?: AgentVerification;
}

// Auth types
export interface AuthUser {
  id: string;
  email: string;
  name?: string;
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
  sources: ChatSource[];
}

export interface DeleteResponse {
  success: boolean;
  message: string;
}
