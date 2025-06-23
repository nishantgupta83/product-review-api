import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState(null);

  const getSentimentColor = (value) => {
    if (value >= 70) return "text-green-600";
    if (value >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post("https://product-review-api-hj41.onrender.com/api/review", {
        url,
      });
      setInsights(response.data);
    } catch (err) {
      console.error("Error fetching insights", err);
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Product Review Insight Extractor</h1>
      <div className="flex gap-4 mb-6">
        <input
          className="border p-2 rounded w-full"
          type="text"
          placeholder="Enter product URL (e.g., Amazon)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {insights && (
        <div className="grid gap-4">
          <div className="bg-white p-4 shadow rounded">
            <h2 className="text-xl font-semibold mb-2">Top 5 Product Enhancement Opportunities</h2>
            <ul className="list-disc pl-6">
              {insights.enhancements.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-4 shadow rounded">
            <h2 className="text-xl font-semibold mb-2">Category-wise Product Sentiment</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(insights.categories).map(([cat, score], i) => (
                <div key={i} className="flex flex-col items-center">
                  <div className={`text-lg font-medium ${getSentimentColor(score)}`}>{cat}</div>
                  <div className="text-3xl font-bold">{score}%</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-4 shadow rounded">
            <h2 className="text-xl font-semibold mb-2">Top 5 Sources</h2>
            <ul className="list-decimal pl-6">
              {insights.sources.map((src, i) => (
                <li key={i}>
                  <a
                    href={src.url}
                    className="text-blue-600 underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {src.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
