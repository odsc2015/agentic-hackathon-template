import Image from "next/image";

interface RecommendedCardProps {
  title: string;
  desc: string;
  img?: string;
}

export default function RecommendedCard({ title, desc, img }: RecommendedCardProps) {
  return (
    <div className="bg-pink-100 rounded-xl p-4 min-w-[220px] flex justify-center flex-col  shadow-sm">
      {img && (
        <div className="mb-3 w-full h-50 relative">
          <Image src={img} alt={title} fill style={{ objectFit: "cover"}} className="object-cover rounded-xl" />
        </div>
      )}
      <strong className="text-base mb-2">{title}</strong>
      <p className="text-pink-700 text-sm">{desc}</p>
    </div>
  );
}
