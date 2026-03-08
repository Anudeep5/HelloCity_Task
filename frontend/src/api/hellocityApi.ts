import type { ChatRequest, ChatResponse, FeedbackRequest } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string;

async function postJSON<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`Request failed ${r.status}: ${text}`);
  }

  return (await r.json()) as TRes;
}

export function postChat(req: ChatRequest): Promise<ChatResponse> {
  return postJSON<ChatRequest, ChatResponse>("/api/chat", req);
}

export function postFeedback(req: FeedbackRequest): Promise<ChatResponse> {
  return postJSON<FeedbackRequest, ChatResponse>("/api/feedback", req);
}

export function postReset(session_id: string): Promise<{ ok: boolean }> {
  return postJSON<{ session_id: string }, { ok: boolean }>("/api/reset", { session_id });
}