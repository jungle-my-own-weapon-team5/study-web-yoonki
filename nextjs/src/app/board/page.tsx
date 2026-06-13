"use client";

import { ArrowLeft, ArrowRight, Plus } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

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
import { fetchBoards } from "@/lib/board-api";
import type { BoardListResponse, BoardSearchType } from "@/types/board";

const PAGE_SIZE = 10;
const SEARCH_DEBOUNCE_MS = 300;

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function useDebouncedValue(value: string, delay: number) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [delay, value]);

  return debouncedValue;
}

export default function BoardListPage() {
  const [page, setPage] = useState(1);
  const [searchType, setSearchType] = useState<BoardSearchType>("title");
  const [keyword, setKeyword] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState<BoardListResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const debouncedKeyword = useDebouncedValue(keyword, SEARCH_DEBOUNCE_MS);
  const debouncedTagFilter = useDebouncedValue(tagFilter, SEARCH_DEBOUNCE_MS);

  const totalPages = useMemo(() => {
    if (!data) {
      return 1;
    }

    return Math.max(1, Math.ceil(data.total / data.size));
  }, [data]);

  useEffect(() => {
    let isActive = true;

    fetchBoards(page, PAGE_SIZE, {
      search_type: searchType,
      keyword: debouncedKeyword.trim(),
      tag: debouncedTagFilter.trim(),
      start_date: startDate,
      end_date: endDate,
    })
      .then((response) => {
        if (!isActive) {
          return;
        }
        setData(response);
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
        setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [debouncedKeyword, debouncedTagFilter, endDate, page, searchType, startDate]);

  const resetToFirstPage = () => {
    setIsLoading(true);
    setPage(1);
  };

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">게시글</h1>
          <p className="text-sm text-muted-foreground">최근 작성된 게시글을 확인합니다.</p>
        </div>
        <Button asChild>
          <Link href="/board/new">
            <Plus />
            작성
          </Link>
        </Button>
      </div>

      <div className="grid gap-3 rounded-md border bg-background p-4 sm:grid-cols-[140px_1fr]">
        <div className="flex flex-col gap-2">
          <Label htmlFor="search-type">검색 대상</Label>
          <Select
            id="search-type"
            value={searchType}
            onChange={(event) => {
              resetToFirstPage();
              setSearchType(event.target.value as BoardSearchType);
            }}
          >
            <option value="title">제목</option>
            <option value="content">내용</option>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="keyword">검색어</Label>
          <Input
            id="keyword"
            value={keyword}
            onChange={(event) => {
              resetToFirstPage();
              setKeyword(event.target.value);
            }}
          />
        </div>
        <div className="flex flex-col gap-2 sm:col-span-2">
          <Label htmlFor="tag">태그</Label>
          <Input
            id="tag"
            placeholder="#react"
            value={tagFilter}
            onChange={(event) => {
              resetToFirstPage();
              setTagFilter(event.target.value);
            }}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="start-date">시작일</Label>
          <Input
            id="start-date"
            type="date"
            value={startDate}
            onChange={(event) => {
              resetToFirstPage();
              setStartDate(event.target.value);
            }}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="end-date">종료일</Label>
          <Input
            id="end-date"
            type="date"
            value={endDate}
            onChange={(event) => {
              resetToFirstPage();
              setEndDate(event.target.value);
            }}
          />
        </div>
      </div>

      {errorMessage && <p className="text-sm text-destructive">{errorMessage}</p>}

      {isLoading ? (
        <Card>
          <CardContent>게시글을 불러오는 중입니다.</CardContent>
        </Card>
      ) : data && data.items.length > 0 ? (
        <div className="flex flex-col gap-3">
          {data.items.map((board) => (
            <Card key={board.id}>
              <CardHeader>
                <CardTitle>
                  <Link className="hover:underline" href={`/board/${board.id}`}>
                    {board.title}
                  </Link>
                </CardTitle>
                <CardDescription>
                  {board.category.title} · 작성자 #{board.author_id} · {formatDate(board.created_at)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  <p className="line-clamp-2 text-sm text-muted-foreground">{board.content}</p>
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
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent>아직 게시글이 없습니다.</CardContent>
        </Card>
      )}

      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          type="button"
          disabled={page <= 1 || isLoading}
          onClick={() => {
            setIsLoading(true);
            setPage((current) => Math.max(1, current - 1));
          }}
        >
          <ArrowLeft />
          이전
        </Button>
        <span className="text-sm text-muted-foreground">
          {page} / {totalPages}
        </span>
        <Button
          variant="outline"
          type="button"
          disabled={page >= totalPages || isLoading}
          onClick={() => {
            setIsLoading(true);
            setPage((current) => current + 1);
          }}
        >
          다음
          <ArrowRight />
        </Button>
      </div>
    </main>
  );
}
