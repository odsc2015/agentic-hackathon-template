import Image from "next/image";

interface TopicCardProps {
  title: string;
  desc: string;
  img?: string;
}

export default function TopicCard({ title, desc, img }: TopicCardProps) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-md flex flex-col items-start">
      {img && (
        <div className="mb-4 w-12 h-12 relative">
          <Image src={img} alt={title} fill style={{ objectFit: "contain" }} />
        </div>
      )}
      <strong className="text-lg mb-2">{title}</strong>
      <p className="text-gray-600 text-sm">{desc}</p>
    </div>
  );
}
