export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'reviewer';
  created_at: string;
}

export interface Candidate {
  id: number;
  name: string;
  email: string;
  role_applied: string;
  status: 'new' | 'reviewed' | 'hired' | 'rejected';
  skills: string[];
  internal_notes?: string;
  ai_summary?: string;
  created_at: string;
}

export interface Score {
  id: number;
  category: string;
  score: number;
  note?: string;
  reviewer_id: number;
  reviewer_name: string;
  created_at: string;
}

export interface CandidateWithScores extends Candidate {
  scores: Score[];
}

export interface CandidateListResponse {
  message: string;
  data: {
    items: Candidate[];
    total: number;
    page: number;
    page_size: number;
  };
}

export interface CandidateDetailResponse {
  message: string;
  data: CandidateWithScores;
}

export interface LoginResponse {
  message: string;
  data: {
    access_token: string;
    token_type: string;
    user: User;
  };
}

export interface LoginData {
  email: string;
  password: string;
}

export interface ScoreCreateData {
  category: string;
  score: number;
  note?: string;
}

export type CandidateStatus = 'new' | 'reviewed' | 'hired' | 'rejected';
