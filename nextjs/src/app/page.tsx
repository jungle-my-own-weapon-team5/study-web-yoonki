import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-10">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Study Web</CardTitle>
          <CardDescription>게시글을 작성하고 목록을 확인합니다.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Button asChild>
            <Link href="/board">게시글 보기</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/board/new">게시글 작성</Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
