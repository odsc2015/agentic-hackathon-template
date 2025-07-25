import Image from "next/image";

const Navbar = () => {
  return (
    <nav className="min-w-screen">
      <div>
        <Image
          src="/logo.png"
          alt="Logo"
          width={100}
          height={50}
          className="mx-auto my-4"
        />
      </div>
    </nav>
  );
}

export default Navbar;
