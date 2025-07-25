// app/login/page.tsx
'use client';

import React from 'react';

export default function LoginPage() {
  return (
    <div
      className="relative flex min-h-screen flex-col bg-[#f8fcfa] overflow-x-hidden"
      style={{ fontFamily: 'Manrope, Noto Sans, sans-serif' }}
    >
      <div className="flex h-full grow flex-col">
        <div className="px-40 flex flex-1 justify-center py-5">
          <div className="flex flex-col w-[512px] max-w-[512px] py-5 max-w-[960px] flex-1">
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
            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
              <label className="flex flex-col min-w-40 flex-1">
                <input
                  type="email"
                  placeholder="Email"
                  className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0c1c17] focus:outline-0 focus:ring-0 border-none bg-[#e6f4ef] focus:border-none h-14 placeholder:text-[#46a080] p-4 text-base font-normal leading-normal"
                  value=""
                  readOnly
                />
              </label>
            </div>
            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
              <label className="flex flex-col min-w-40 flex-1">
                <input
                  type="password"
                  placeholder="Password"
                  className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0c1c17] focus:outline-0 focus:ring-0 border-none bg-[#e6f4ef] focus:border-none h-14 placeholder:text-[#46a080] p-4 text-base font-normal leading-normal"
                  value=""
                  readOnly
                />
              </label>
            </div>
            <p className="text-[#46a080] text-sm font-normal leading-normal pb-3 pt-1 px-4 underline">
              Forgot Password
            </p>
            <div className="flex px-4 py-3">
              <button
                className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-12 px-5 flex-1 bg-[#019863] text-[#f8fcfa] text-base font-bold leading-normal tracking-[0.015em]"
              >
                <span className="truncate">Login</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
