// App structure
// - InputForm: Get product URL
// - Dashboard: Display extracted review insights
// - Real backend API support with scraping and NLP

import React, { useState } from "react";
//import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Gauge } from "@/components/ui/gauge";
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
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Product Review Insight Extractor</h1>
      <div className="flex gap-4 mb-6">
        <Input
          type="text"
          placeholder="Enter product URL (e.g., Amazon)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button onClick={handleSubmit} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </Button>
      </div>

      {insights && (
        <div className="grid gap-4">
          <Card>
            <CardContent>
              <h2 className="text-xl font-semibold">Top 5 Product Enhancement Opportunities</h2>
              <ul className="list-disc pl-6">
                {insights.enhancements.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <h2 className="text-xl font-semibold">Category-wise Product Sentiment</h2>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(insights.categories).map(([cat, score], i) => (
                  <div key={i} className="flex flex-col items-center">
                    <div className={`text-lg font-medium ${getSentimentColor(score)}`}>{cat}</div>
                    <Gauge value={score} className="w-32 h-32" />
                    <div className="mt-2 text-sm">{score}%</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <h2 className="text-xl font-semibold mb-2">Top 5 Sources</h2>
              <ul className="list-decimal pl-6 space-y-2">
                {insights.sources.map((src, i) => (
                  <li key={i}>
                    <div className="flex flex-col">
                      <a href={src.url} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">{src.name}</a>
                      {src.snippet && (
                        <button
                          className="text-xs text-gray-700 underline mt-1 text-left"
                          onClick={() => alert(src.snippet)}
                        >
                          View Summary
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
