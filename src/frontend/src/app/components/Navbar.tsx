"use client";
import Link from "next/link";
import { Bell } from "lucide-react";
import { useState } from "react";

const Navbar = () => {
	const [bellWindow, setBellWindow] = useState(false);
	return (
		<header className="flex justify-between items-center px-6 py-4 bg-white shadow">
			<div className="font-bold text-lg">
				<img src="/Logo.png" alt="" />
			</div>
			<nav className="flex gap-20 items-center">
				<Link href="/DayOverview" className="text-gray-600 hover:text-black">
					Today
				</Link>
				<Link href="/Learn" className="text-gray-600 hover:text-black">
					Learn
				</Link>
				<Link href="/Chat" className="text-gray-600 hover:text-black">
          Chat 
        </Link>
				<Link href="/PartnerTip" className="text-gray-600 hover:text-black">
					Partner Tips
				</Link>
				<div
					className="relative cursor-pointer"
					onClick={() => setBellWindow(!bellWindow)}
				>
					<Bell />

					{bellWindow && (
						<div className="absolute right-0 top-full mt-2 w-64 bg-white shadow-lg rounded-lg p-4 z-50">
							<p className="text-gray-700">No new notifications</p>
						</div>
					)}
				</div>

				<div className="w-8 h-8 bg-gray-300 rounded-full border-2 border-blue-200 flex items-center justify-center overflow-hidden">
					<span role="img" aria-label="User">
						👩
					</span>
				</div>
			</nav>
		</header>
	);
};

export default Navbar;
