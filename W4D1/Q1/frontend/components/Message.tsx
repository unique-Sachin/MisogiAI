"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

interface Props {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export default function Message({ role, content, sources }: Props) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          `max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap text-sm shadow ` +
          (isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-100 dark:bg-zinc-800 dark:text-gray-200 rounded-bl-none")
        }
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            a: (props) => <a className="text-blue-500 underline" {...props} />,
            code: ({ inline, className, children, ...props }: any) => (
              <code
                className={
                  "rounded px-1 py-0.5 " +
                  (inline ? "bg-gray-200 dark:bg-zinc-700" : className)
                }
                {...props}
              >
                {children}
              </code>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
        {sources && sources.length > 0 && !isUser && (
          <p className="mt-2 text-[10px] text-gray-500">Sources: {sources.join(", ")}</p>
        )}
      </div>
    </div>
  );
} 