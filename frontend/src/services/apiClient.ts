export async function callAgentAPI(userInput: string) {
  const url = `${process.env.NEXT_PUBLIC_AGENT_API_URL}/react`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: userInput }),
  });
  return response.json();
}