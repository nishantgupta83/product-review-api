// src/components/ui/card.jsx
export function Card({ children }) {
  return <div className="rounded-2xl border p-4 shadow">{children}</div>;
}

export function CardContent({ children }) {
  return <div className="mt-2">{children}</div>;
}
