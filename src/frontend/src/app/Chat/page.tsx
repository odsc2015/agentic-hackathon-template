import GeminiChat from "../components/GeminiChat";

export default function ChatPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Chat with Gemini</h1>
      <GeminiChat />
    </div>
  );
}