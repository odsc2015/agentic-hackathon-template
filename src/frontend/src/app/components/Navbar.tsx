import Image from "next/image";

const Navbar = () => {
  return (
     <header className="flex justify-between items-center px-6 py-4 bg-white shadow">
        <div className="font-bold text-lg">
          <img src="/Logo.png" alt="" />
        </div>
        <nav className="flex gap-20 items-center">
          <a href="#" className="text-gray-600 hover:text-black">Today</a>
          <a href="#" className="text-gray-600 hover:text-black">Calendar</a>
          <a href="#" className="text-gray-600 hover:text-black">Insights</a>
          <a href="#" className="text-gray-600 hover:text-black">Community</a>

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
