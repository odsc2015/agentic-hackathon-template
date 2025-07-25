'use client';

import { signIn } from "next-auth/react";

export default function LoginButton(color: string ) {
  return (
    <div className="flex flex-col items-center justify-center">
      <button
        className="px-6 py-2 bg-blue-600 text-white rounded"
        onClick={() => signIn("google")}
      >
        Sign in with Google
      </button>
    </div>
  );
}
