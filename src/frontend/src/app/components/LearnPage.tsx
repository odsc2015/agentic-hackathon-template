"use client"
import RecommendedCard from "../components/RecommendedCard";
import { useState, ChangeEvent } from "react";
import TopicCard from "../components/TopicCard";
import Image from "next/image";

interface Topic {
  id: number;
  title: string;
  desc: string;
  category: string;
  img?: string;
}

const allTopics: Topic[] = [
  { id: 1, title: "Understanding Your Cycle", desc: "A comprehensive guide...", category: "Cycle Phases" },
  { id: 2, title: "The Menstrual Phase", desc: "What happens during menstruation.", category: "Cycle Phases" },
  { id: 3, title: "The Follicular Phase", desc: "The phase leading up to ovulation.", category: "Cycle Phases" },
  { id: 4, title: "The Ovulatory Phase", desc: "The peak fertility window.", category: "Cycle Phases" },
  { id: 5, title: "The Luteal Phase", desc: "The phase after ovulation.", category: "Cycle Phases" },
  { id: 6, title: "Hormonal Fluctuations", desc: "How hormones change throughout the cycle.", category: "Hormonal Changes" },
  { id: 7, title: "Estrogen's Role", desc: "The hormone that peaks before ovulation.", category: "Hormonal Changes" },
  { id: 8, title: "Progesterone's Influence", desc: "The hormone that rises after ovulation.", category: "Hormonal Changes" },
  { id: 9, title: "Self-Care Strategies", desc: "Practices to support well-being.", category: "Self-Care" },
  { id: 10, title: "Stress Management", desc: "Techniques to reduce stress.", category: "Self-Care" },
  { id: 11, title: "Sleep Optimization", desc: "Tips for better sleep.", category: "Self-Care" },
  { id: 12, title: "Nutrition for Cycle Support", desc: "Dietary recommendations for cycle health.", category: "Self-Care" },
];

const recommended: Topic[] = [
  { id: 1, title: "Mindfulness for Cycle Harmony", desc: "Discover mindfulness techniques...", img: "/mindfulness.png", category: "" },
  { id: 2, title: "Cycle-Syncing Workouts", desc: "Tailor your workouts to match your cycle...", img: "/workouts.png", category: "" },
  { id: 3, title: "Nourishing Your Body Through Each Phase", desc: "Learn how to adjust your diet...", img: "/nourish.png", category: "" },
];

const categories = ["All", "Cycle Phases", "Hormonal Changes", "Self-Care"] as const;
type Category = typeof categories[number];

export default function Learn() {
  const [selectedCategory, setSelectedCategory] = useState<Category>("All");
  const [search, setSearch] = useState("");

  const filteredTopics = allTopics.filter(topic =>
    (selectedCategory === "All" || topic.category === selectedCategory) &&
    (topic.title.toLowerCase().includes(search.toLowerCase()) || topic.desc.toLowerCase().includes(search.toLowerCase()))
  );

  function handleSearchChange(e: ChangeEvent<HTMLInputElement>) {
    setSearch(e.target.value);
  }

  return (
    <div className="p-8 font-sans bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Learn</h1>

      <input
        type="text"
        placeholder="Search"
        value={search}
        onChange={handleSearchChange}
        className="w-full p-2 mb-8 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-pink-400"
      />

      <h2 className="text-2xl font-semibold mb-4">Recommended for you</h2>
      <div className="flex gap-4 mb-8 flex-wrap">
        {recommended.map(rec => (
          <RecommendedCard key={rec.id} {...rec} />
        ))}
      </div>

      <h2 className="text-2xl font-semibold mb-4">All Topics</h2>
      <div className="flex gap-3 mb-6 flex-wrap">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-full font-medium transition-colors
              ${selectedCategory === cat ? "bg-pink-400 text-white" : "bg-gray-200 text-gray-700 hover:bg-pink-100"}`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(260px,1fr))]">
        {filteredTopics.map(topic => (
          <TopicCard key={topic.id} {...topic} />
        ))}
      </div>
    </div>
  );
}
