import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import "./NotePreview.css";

export default function NotePreview({ note }) {
  return (
    <div>
      <h1 className="fw-bold">{note.title}</h1>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: "h2",
          h2: "h3",
          h3: "h4",
          h4: "h5",
          input({ node, ...props }) {
            const newProps = {
              ...props,
              disabled: undefined,
              onChange: () => {
                console.log(node);
              },
            };
            return <input {...newProps} />;
          },
        }}
      >
        {note.content}
      </ReactMarkdown>
    </div>
  );
}
