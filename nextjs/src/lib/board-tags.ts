import type { Tag } from "@/types/board";

export function parseTagInput(value: string): string[] {
  const tags: string[] = [];
  const seenTags = new Set<string>();

  value.split(/\s+/).forEach((token) => {
    const tag = token.trim().replace(/^#+/, "").trim();

    if (!tag || seenTags.has(tag)) {
      return;
    }

    tags.push(tag);
    seenTags.add(tag);
  });

  return tags;
}

export function formatTagInput(tags: Tag[]): string {
  return tags.map((tag) => `#${tag.title}`).join(" ");
}
