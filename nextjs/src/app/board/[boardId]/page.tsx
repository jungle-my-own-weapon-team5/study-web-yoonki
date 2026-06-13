"use client";

import { ArrowLeft, ChevronLeft, ChevronRight, Pencil, Save, Trash2, X } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  deleteBoard,
  fetchBoard,
  fetchBoardNeighbors,
  fetchCategories,
  updateBoard,
} from "@/lib/board-api";
import { formatTagInput, parseTagInput } from "@/lib/board-tags";
import { useAuthStore } from "@/stores/auth";
import type { Board, BoardNeighbors, Category } from "@/types/board";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function BoardDetailPage() {
  const params = useParams<{ boardId: string }>();
  const router = useRouter();
  const { user, isLoading: isAuthLoading } = useAuthStore();
  const boardId = Number(params?.boardId ?? 0);
  const [board, setBoard] = useState<Board | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [tagsInput, setTagsInput] = useState("");
  const [neighbors, setNeighbors] = useState<BoardNeighbors | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isCategoryLoading, setIsCategoryLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const canManage = Boolean(!isAuthLoading && user && board && user.id === board.author_id);

  useEffect(() => {
    let isActive = true;

    Promise.all([fetchBoard(boardId), fetchBoardNeighbors(boardId), fetchCategories()])
      .then(([data, neighborData, categoryData]) => {
        if (!isActive) {
          return;
        }

        setBoard(data);
        setTitle(data.title);
        setContent(data.content);
        setCategoryId(String(data.category_id));
        setTagsInput(formatTagInput(data.tags));
        setNeighbors(neighborData);
        setCategories(categoryData);
        setErrorMessage("");
      })
      .catch((error) => {
        if (!isActive) {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "게시글을 불러오지 못했습니다.");
      })
      .finally(() => {
        if (!isActive) {
          return;
        }
        setIsCategoryLoading(false);
        setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [boardId]);

  const onUpdate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!canManage) {
      setErrorMessage("게시글 수정 권한이 없습니다.");
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const updatedBoard = await updateBoard(boardId, {
        title,
        content,
        category_id: Number(categoryId),
        tags: parseTagInput(tagsInput),
      });
      setBoard(updatedBoard);
      setTagsInput(formatTagInput(updatedBoard.tags));
      setIsEditing(false);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "게시글을 수정하지 못했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const onCancelEdit = () => {
    if (board) {
      setTitle(board.title);
      setContent(board.content);
      setCategoryId(String(board.category_id));
      setTagsInput(formatTagInput(board.tags));
    }

    setIsEditing(false);
  };

  const onDelete = async () => {
    if (!canManage) {
      setErrorMessage("게시글 삭제 권한이 없습니다.");
      return;
    }

    const confirmed = window.confirm("게시글을 삭제할까요?");

    if (!confirmed) {
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await deleteBoard(boardId);
      router.push("/board");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "게시글을 삭제하지 못했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-2xl px-6 py-10">
        <Card>
          <CardContent>게시글을 불러오는 중입니다.</CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-6 py-10">
      <Button asChild className="w-fit" variant="ghost">
        <Link href="/board">
          <ArrowLeft />
          목록
        </Link>
      </Button>

      {errorMessage && <p className="text-sm text-destructive">{errorMessage}</p>}

      {board ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{isEditing ? "게시글 수정" : board.title}</CardTitle>
            <CardDescription>
              {board.category.title} · 작성자 #{board.author_id} · {formatDate(board.created_at)}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              <form className="flex flex-col gap-5" onSubmit={onUpdate}>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="title">제목</Label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="category-id">카테고리</Label>
                  <Select
                    id="category-id"
                    value={categoryId}
                    onChange={(event) => setCategoryId(event.target.value)}
                    disabled={isCategoryLoading || categories.length === 0}
                  >
                    {categories.length === 0 ? (
                      <option value="">카테고리 없음</option>
                    ) : (
                      categories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.title}
                        </option>
                      ))
                    )}
                  </Select>
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="content">내용</Label>
                  <Textarea
                    id="content"
                    value={content}
                    onChange={(event) => setContent(event.target.value)}
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="tags">태그</Label>
                  <Input
                    id="tags"
                    placeholder="#react #fastapi"
                    value={tagsInput}
                    onChange={(event) => setTagsInput(event.target.value)}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    className="flex-1"
                    type="submit"
                    disabled={!title || !content || !categoryId || isSubmitting || categories.length === 0}
                  >
                    <Save />
                    저장
                  </Button>
                  <Button
                    className="flex-1"
                    type="button"
                    variant="outline"
                    onClick={onCancelEdit}
                  >
                    <X />
                    취소
                  </Button>
                </div>
              </form>
            ) : (
              <div className="flex flex-col gap-6">
                <p className="whitespace-pre-wrap text-sm leading-6">{board.content}</p>
                {board.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {board.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground"
                      >
                        #{tag.title}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={!canManage}
                    onClick={() => setIsEditing(true)}
                  >
                    <Pencil />
                    수정
                  </Button>
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    disabled={!canManage || isSubmitting}
                    onClick={onDelete}
                  >
                    <Trash2 />
                    삭제
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent>게시글을 찾을 수 없습니다.</CardContent>
        </Card>
      )}

      {board && neighbors && (
        <nav className="grid gap-3 sm:grid-cols-2">
          <div className="flex min-h-20 flex-col justify-between rounded-md border bg-background p-3">
            <span className="text-xs text-muted-foreground">이전 글</span>
            {neighbors.previous ? (
              <Link
                className="mt-2 inline-flex items-center gap-1 text-sm font-medium hover:underline"
                href={`/board/${neighbors.previous.id}`}
              >
                <ChevronLeft />
                {neighbors.previous.title}
              </Link>
            ) : (
              <span className="mt-2 text-sm text-muted-foreground">이전 글이 없습니다.</span>
            )}
          </div>
          <div className="flex min-h-20 flex-col justify-between rounded-md border bg-background p-3 sm:text-right">
            <span className="text-xs text-muted-foreground">다음 글</span>
            {neighbors.next ? (
              <Link
                className="mt-2 inline-flex items-center gap-1 text-sm font-medium hover:underline sm:justify-end"
                href={`/board/${neighbors.next.id}`}
              >
                {neighbors.next.title}
                <ChevronRight />
              </Link>
            ) : (
              <span className="mt-2 text-sm text-muted-foreground">다음 글이 없습니다.</span>
            )}
          </div>
        </nav>
      )}
    </main>
  );
}
