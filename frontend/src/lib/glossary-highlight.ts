import type { Element, Root, Text, ElementContent } from "hast";
import type { Plugin } from "unified";

export type GlossaryHighlightEntry = {
  source_term: string;
  translation: string;
};

type TermMatch = {
  pattern: string;
  sourceTerms: string[];
};

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function buildTermMatches(
  entries: GlossaryHighlightEntry[]
): TermMatch[] {
  const byKey = new Map<
    string,
    { pattern: string; sourceTerms: Set<string> }
  >();

  for (const entry of entries) {
    const pattern = entry.translation.trim();
    if (!pattern) continue;
    const key = pattern.toLowerCase();
    const existing = byKey.get(key);
    if (existing) {
      existing.sourceTerms.add(entry.source_term);
    } else {
      byKey.set(key, {
        pattern,
        sourceTerms: new Set([entry.source_term]),
      });
    }
  }

  return [...byKey.values()]
    .map(({ pattern, sourceTerms }) => ({
      pattern,
      sourceTerms: [...sourceTerms],
    }))
    .sort((a, b) => b.pattern.length - a.pattern.length);
}

export function buildGlossaryRegex(matches: TermMatch[]): RegExp | null {
  if (matches.length === 0) return null;
  const alternation = matches.map((m) => escapeRegex(m.pattern)).join("|");
  return new RegExp(`\\b(?:${alternation})\\b`, "gi");
}

function findMatch(matchedText: string, matches: TermMatch[]): TermMatch | undefined {
  const lower = matchedText.toLowerCase();
  return matches.find((m) => m.pattern.toLowerCase() === lower);
}

function splitTextNode(
  text: string,
  regex: RegExp,
  matches: TermMatch[]
): ElementContent[] {
  const nodes: ElementContent[] = [];
  let lastIndex = 0;
  const re = new RegExp(regex.source, regex.flags);

  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    const start = match.index;
    const end = start + match[0].length;

    if (start > lastIndex) {
      nodes.push({ type: "text", value: text.slice(lastIndex, start) });
    }

    const matchedText = match[0];
    const termMatch = findMatch(matchedText, matches);

    nodes.push({
      type: "element",
      tagName: "mark",
      properties: {
        className: ["glossary-highlight"],
        dataSourceTerms: (termMatch?.sourceTerms ?? []).join("\n"),
      },
      children: [{ type: "text", value: matchedText }],
    });

    lastIndex = end;
    if (match[0].length === 0) {
      re.lastIndex += 1;
    }
  }

  if (lastIndex < text.length) {
    nodes.push({ type: "text", value: text.slice(lastIndex) });
  }

  return nodes;
}

function processElement(element: Element, regex: RegExp, matches: TermMatch[], inCode: boolean) {
  const skip = inCode || element.tagName === "code" || element.tagName === "pre";
  const children = element.children;

  for (let i = 0; i < children.length; i++) {
    const child = children[i];
    if (child.type === "element") {
      processElement(child, regex, matches, skip);
    } else if (child.type === "text" && !skip && child.value.trim()) {
      const replacement = splitTextNode(child.value, regex, matches);
      if (replacement.length === 1 && replacement[0].type === "text") continue;
      children.splice(i, 1, ...replacement);
      i += replacement.length - 1;
    }
  }
}

export function createGlossaryHighlightPlugin(
  entries: GlossaryHighlightEntry[]
): Plugin<[], Root> {
  const matches = buildTermMatches(entries);
  const regex = buildGlossaryRegex(matches);

  return function glossaryHighlightPlugin() {
    return (tree: Root) => {
      if (!regex) return;
      for (const child of tree.children) {
        if (child.type === "element") {
          processElement(child, regex, matches, false);
        }
      }
    };
  };
}
