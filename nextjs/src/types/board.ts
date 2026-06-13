export type Category = {
  id: number;
  title: string;
};

export type Tag = {
  id: number;
  title: string;
};

export type Board = {
  id: number;
  title: string;
  content: string;
  author_id: number;
  category_id: number;
  category: Category;
  tags: Tag[];
  created_at: string;
  updated_at: string | null;
};

export type BoardListResponse = {
  items: Board[];
  page: number;
  size: number;
  total: number;
};

export type BoardCreatePayload = {
  title: string;
  content: string;
  category_id: number;
  tags?: string[];
};

export type BoardUpdatePayload = Partial<BoardCreatePayload>;

export type BoardSearchType = "title" | "content";

export type BoardListFilters = {
  search_type?: BoardSearchType;
  keyword?: string;
  tag?: string;
  start_date?: string;
  end_date?: string;
};

export type BoardSummary = {
  id: number;
  title: string;
  created_at: string;
};

export type BoardNeighbors = {
  previous: BoardSummary | null;
  next: BoardSummary | null;
};
