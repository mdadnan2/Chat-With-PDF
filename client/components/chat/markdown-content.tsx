/* eslint-disable @typescript-eslint/no-unused-vars -- ReactMarkdown's AST node must be omitted before forwarding props to HTML. */
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

function normalizeMarkdown(content: string): string {
    let insideTable = false;
    const normalizedLines = content.split(/\r?\n/).map((line) => {
        if (/^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line)) {
            insideTable = true;
        } else if (insideTable && line.trim() && !line.includes("|")) {
            insideTable = false;
        }

        const normalizedLine = line.replace(/<br\s*\/?>/gi, insideTable ? " / " : "  \n");
        if (!line.trim()) insideTable = false;
        return normalizedLine;
    }).join("\n");

    return normalizedLines.replace(/(^|\n)([ \t]*)[•●▪◦][ \t]+/g, "$1$2- ");
}

const MARKDOWN_COMPONENTS: Components = {
    h1: ({ node: _node, ...props }) => (
        <h1 {...props} className="mb-2 mt-4 text-lg font-semibold leading-snug first:mt-0" />
    ),
    h2: ({ node: _node, ...props }) => (
        <h2 {...props} className="mb-2 mt-4 text-base font-semibold leading-snug first:mt-0" />
    ),
    h3: ({ node: _node, ...props }) => (
        <h3 {...props} className="mb-1 mt-3 text-sm font-semibold leading-snug first:mt-0" />
    ),
    h4: ({ node: _node, ...props }) => (
        <h4 {...props} className="mb-1 mt-3 text-sm font-semibold leading-snug first:mt-0" />
    ),
    p: ({ node: _node, ...props }) => (
        <p {...props} className="my-2 leading-relaxed first:mt-0 last:mb-0" />
    ),
    ul: ({ node: _node, ...props }) => (
        <ul {...props} className="my-2 list-disc space-y-1 pl-5 leading-relaxed [&_ol]:my-1 [&_ul]:my-1" />
    ),
    ol: ({ node: _node, ...props }) => (
        <ol {...props} className="my-2 list-decimal space-y-1 pl-5 leading-relaxed [&_ol]:my-1 [&_ul]:my-1" />
    ),
    li: ({ node: _node, ...props }) => (
        <li {...props} className="pl-1 leading-relaxed marker:text-muted-foreground" />
    ),
    blockquote: ({ node: _node, ...props }) => (
        <blockquote {...props} className="my-3 border-l-2 border-border pl-3 text-muted-foreground" />
    ),
    table: ({ node: _node, ...props }) => (
        <div className="my-3 max-w-full overflow-x-auto rounded-md border border-border">
            <table {...props} className="w-full min-w-[32rem] border-collapse text-left text-xs" />
        </div>
    ),
    thead: ({ node: _node, ...props }) => (
        <thead {...props} className="bg-muted/70" />
    ),
    th: ({ node: _node, ...props }) => (
        <th {...props} className="border-b border-border px-3 py-2 font-semibold text-foreground" />
    ),
    td: ({ node: _node, ...props }) => (
        <td {...props} className="border-b border-border px-3 py-2 align-top last:border-b-0" />
    ),
    tr: ({ node: _node, ...props }) => (
        <tr {...props} className="even:bg-muted/30" />
    ),
    code: ({ node: _node, ...props }) => (
        <code {...props} className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]" />
    ),
    pre: ({ node: _node, ...props }) => (
        <pre
            {...props}
            className="my-3 max-w-full overflow-x-auto rounded-md border border-border bg-muted p-3 text-xs leading-relaxed [&_code]:rounded-none [&_code]:bg-transparent [&_code]:p-0"
        />
    ),
    hr: ({ node: _node, ...props }) => (
        <hr {...props} className="my-4 border-border" />
    ),
};

export function MarkdownContent({
    content,
    className = "",
}: {
    content: string;
    className?: string;
}) {
    return (
        <div className={className}>
            <ReactMarkdown
                components={MARKDOWN_COMPONENTS}
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
            >
                {normalizeMarkdown(content)}
            </ReactMarkdown>
        </div>
    );
}
