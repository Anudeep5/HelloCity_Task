export type Role = "user" | "assistant";

export type ChatMessage = {
  role: Role;
  text: string;
};

export type PlaceCard = {
  name: string;
  address?: string | null;
  rating?: number | null;
  user_ratings_total?: number | null;
  maps_url?: string | null;
  photo_url?: string | null;
};

export type ChatResponse = {
  assistant_message: string;
  interests: string[];
  interest_detected: boolean;
  interest_added?: string | null;
  examples?: PlaceCard[] | null;
  onboarding_complete: boolean;
  profile?: { interests: string[] } | null;
};

export type ChatRequest = {
  session_id: string;
  message: string;
};

export type FeedbackRequest = {
  session_id: string;
  interest: string;
  choice: "yes" | "no";
};