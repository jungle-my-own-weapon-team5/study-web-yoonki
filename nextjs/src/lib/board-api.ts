import { API_BASE_URL } from "@/config";
import type {
  Board,
  BoardCreatePayload,
  BoardListFilters,
  BoardListResponse,
  BoardNeighbors,
  BoardUpdatePayload,
  Category,
} from "@/types/board";

type ApiErrorBody = {
  detail?: string;
};

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const body = (await response.json()) as ApiErrorBody;
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function fetchBoards(
  page: number,
  size: number,
  filters: BoardListFilters = {},
): Promise<BoardListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    size: String(size),
  });

  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  return requestJson<BoardListResponse>(`${API_BASE_URL}/board/?${params}`);
}

export function fetchCategories(): Promise<Category[]> {
  return requestJson<Category[]>(`${API_BASE_URL}/board/categories`);
}

export function fetchBoard(boardId: number): Promise<Board> {
  return requestJson<Board>(`${API_BASE_URL}/board/${boardId}`);
}

export function fetchBoardNeighbors(boardId: number): Promise<BoardNeighbors> {
  return requestJson<BoardNeighbors>(`${API_BASE_URL}/board/${boardId}/neighbors`);
}

export function createBoard(payload: BoardCreatePayload): Promise<Board> {
  return requestJson<Board>(`${API_BASE_URL}/board/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateBoard(boardId: number, payload: BoardUpdatePayload): Promise<Board> {
  return requestJson<Board>(`${API_BASE_URL}/board/${boardId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteBoard(boardId: number): Promise<void> {
  await requestJson<{ message: string }>(`${API_BASE_URL}/board/${boardId}`, {
    method: "DELETE",
  });
}
