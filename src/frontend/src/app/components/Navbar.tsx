import Image from "next/image";
import Link from "next/link";

const Navbar = () => {
  return (
     <header className="flex justify-between items-center px-6 py-4 bg-white shadow">
        <div className="font-bold text-lg">
          <img src="/Logo.png" alt="" />
        </div>
        <nav className="flex gap-20 items-center">
          <Link href="/DayOverview" className="text-gray-600 hover:text-black">Today</Link>
          <a href="#" className="text-gray-600 hover:text-black">Calendar</a>
          <a href="#" className="text-gray-600 hover:text-black">Insights</a>
          <Link href="/PartnerTip" className="text-gray-600 hover:text-black">Partner Tips</Link>

          <div className="w-8 h-8 bg-gray-300 rounded-full border-2 border-blue-200 flex items-center justify-center overflow-hidden">
            <span role="img" aria-label="User">

              👩
            </span>
          </div>
        </nav>
      </header>
  );
}

export default Navbar;
