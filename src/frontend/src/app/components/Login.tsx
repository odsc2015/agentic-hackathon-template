// app/login/page.tsx
'use client';

import React from 'react';
import LoginButton from '@/app/components/LoginButton';

export default function LoginPage() {
  return (
    <div
      className="relative flex min-h-screen flex-col bg-[#f8fcfa] overflow-x-hidden"
      style={{ fontFamily: 'Manrope, Noto Sans, sans-serif' }}
    >
      <div className="flex h-full grow flex-col">
        <div className="px-40 flex flex-1 justify-center py-5">
          <div className="flex flex-col w-[512px] max-w-[512px] py-5 flex-1">
            <div className="@container">
              <div className="@[480px]:px-4 @[480px]:py-3">
                <div
                  className="w-full bg-center bg-no-repeat bg-cover flex flex-col justify-end overflow-hidden bg-[#f8fcfa] @[480px]:rounded-xl min-h-80"
                  style={{
                    backgroundImage:
                      'url("https://lh3.googleusercontent.com/aida-public/AB6AXuATI12sPaXNyED_1iltPpFuEWKxIG6TxDPI4lQpPSgw2FD2wTHAjNYYkSA1g_ixfH5CkSRC07_HfPVD1UQLMkfoHOvFO5sUdzUopLPyLvX4HnVlL2G9jQQQ_KbGZ7fs79zKojlf9j5x9sCSJJcAhDwvQiebJ3-B9hPVzC56TxH29j2sozhWtMkpWxlvmBRUBfBKhkrW7Ush2AXEDQMgWvsVmDNrqLVREbowBBv9Ehn6Z1XY1ZMbO3P4S0ueRIThYlB1Ni8qvfMC6rfz")',
                  }}
                />
              </div>
            </div>
            <h2 className="text-[#0c1c17] tracking-light text-[28px] font-bold leading-tight px-4 text-center pb-3 pt-5">
              Welcome to Cyclewise
            </h2>
            <div className="flex px-4 py-3 justify-center gap-3">
              <LoginButton  />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
