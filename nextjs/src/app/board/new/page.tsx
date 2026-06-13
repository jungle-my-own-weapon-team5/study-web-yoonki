"use client";

import { ArrowLeft, Save } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { createBoard, fetchCategories } from "@/lib/board-api";
import { parseTagInput } from "@/lib/board-tags";
import { useAuthStore } from "@/stores/auth";
import type { Category } from "@/types/board";

export default function NewBoardPage() {
  const router = useRouter();
  const { user, isLoading: isAuthLoading, checkAuth } = useAuthStore();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [tagsInput, setTagsInput] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [hasVerifiedAuth, setHasVerifiedAuth] = useState(false);
  const [isCategoryLoading, setIsCategoryLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let isActive = true;

    checkAuth().finally(() => {
      if (isActive) {
        setHasVerifiedAuth(true);
      }
    });

    return () => {
      isActive = false;
    };
  }, [checkAuth]);

  useEffect(() => {
    if (hasVerifiedAuth && !isAuthLoading && !user) {
      router.replace("/auth/login");
    }
  }, [hasVerifiedAuth, isAuthLoading, router, user]);

  useEffect(() => {
    let isActive = true;

    fetchCategories()
      .then((response) => {
        if (!isActive) {
          return;
        }

        setCategories(response);
        setCategoryId((current) => current || String(response[0]?.id ?? ""));
      })
      .catch((error) => {
        if (!isActive) {
          return;
        }

        setErrorMessage(error instanceof Error ? error.message : "카테고리를 불러오지 못했습니다.");
      })
      .finally(() => {
        if (!isActive) {
          return;
        }

        setIsCategoryLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, []);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!user) {
      router.replace("/auth/login");
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const board = await createBoard({
        title,
        content,
        category_id: Number(categoryId),
        tags: parseTagInput(tagsInput),
      });

      router.push(`/board/${board.id}`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "게시글을 생성하지 못했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!hasVerifiedAuth || isAuthLoading || !user) {
    return (
      <main className="mx-auto w-full max-w-2xl px-6 py-10">
        <Card>
          <CardContent>로그인 상태를 확인하는 중입니다.</CardContent>
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

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">게시글 작성</CardTitle>
          <CardDescription>제목과 내용을 입력해 새 게시글을 작성합니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-5" onSubmit={onSubmit}>
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

            {errorMessage && <p className="text-sm text-destructive">{errorMessage}</p>}

            <Button
              className="w-full"
              size="lg"
              type="submit"
              disabled={!title || !content || !categoryId || isSubmitting || categories.length === 0}
            >
              <Save />
              {isSubmitting ? "저장 중..." : "저장"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
