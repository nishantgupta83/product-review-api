// src/components/ui/card.jsx
export function Card({ children }) {
  return <div className="border rounded-xl p-4 shadow">{children}</div>;
}

export function CardContent({ children }) {
  return <div className="mt-2">{children}</div>;
}
