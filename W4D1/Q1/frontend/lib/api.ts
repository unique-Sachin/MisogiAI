export interface ChatResponse {
  answer: string;
  sources?: string[] | null;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error(`Backend error: ${res.status}`);
  }

  return (await res.json()) as ChatResponse;
} 