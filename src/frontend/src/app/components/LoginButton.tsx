'use client';

import { signIn } from "next-auth/react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';

interface LoginButtonProps {
  color?: string;
}

export default function LoginButton() {
  return (
    <div className="flex flex-col items-center justify-center">
      <button
        className={`px-6 py-2 bg-[#009963] text-white rounded hover:cursor-pointer`}
        onClick={() => signIn("google", {callbackUrl: '/DayOverview'})}
      >
        <FontAwesomeIcon icon={faGoogle} className="mr-2" />
        Sign in with Google
      </button>
    </div>
  );
}
