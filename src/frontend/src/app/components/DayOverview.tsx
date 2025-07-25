"use client";
import Image from "next/image";
import { useState } from "react";

const DayOverview = () => {
	const day: number = 1;

	const getPhase = (day: number) => {
		if (day >= 1 && day <= 5) return 1;
		if (day > 5 && day <= 14) return 2;
		if (day > 14 && day <= 21) return 3;
		return 4;
	};

	const phase = getPhase(day);
	return (
		<div>
			<main className="max-w-3xl mx-auto mt-8 px-4">
				<div className="text-md text-[#59808C] mb-2">
					Today / <span className="text-black font-medium">Day {day}</span>
				</div>

				<h1 className="text-3xl pt-4 font-bold mb-2">Day {day}</h1>

				{phase === 1 && (
					<p className="text-black mb-4 pt-4">
						Today is the first day of your period. You may experience cramps,
						fatigue, and mood swings. Remember to be kind to yourself and
						prioritize rest.
					</p>
				)}

				{phase === 2 && (
					<p className="text-black mb-4 pt-4">
						You are in the follicular phase. Your body is preparing for
						ovulation, and you may feel more energetic and optimistic.
					</p>
				)}

				{phase === 3 && (
					<p className="text-black mb-4 pt-4">
						You are in the luteal phase. Hormonal changes may lead to PMS
						symptoms like bloating and mood swings. Stay hydrated and maintain a
						balanced diet.
					</p>
				)}

				{phase === 4 && (
					<p className="text-black mb-4 pt-4">
						You are in the late luteal phase. Your body is preparing for the
						next cycle, and you may experience premenstrual symptoms. Focus on
						self-care and relaxation.
					</p>
				)}

				{/* Cycle Phase Section */}

				<div className="mb-6 flex flex-col gap-6">
					<div className="flex flex-col gap-4 ">
						<div className="text-lg text-gray-700">Cycle Phase</div>
						<div className="text-lg font-semibold ">Menstruation</div>
						<div className="text-sm text-gray-400">Day 1-5</div>
					</div>
					<div className="flex justify-end">
						{phase === 1 && (
							<Image
								src="/Phase 1.jpg"
								alt="Phase 1 Illustration"
								width={400}
								height={300}
								className=" rounded-lg shadow"
							/>
						)}
						{phase === 2 && (
							<Image
								src="/Phase 2.jpg"
								alt="Phase 2 Illustration"
								width={400}
								height={100}
								className="w-full h-auto rounded-lg shadow"
							/>
						)}
						{phase === 3 && (
							<Image
								src="/Phase 3.jpg"
								alt="Phase 3 Illustration"
								width={400}
								height={100}
								className="w-full h-auto rounded-lg shadow"
							/>
						)}
						{phase === 4 && (
							<Image
								src="/Phase 4.jpg"
								alt="Phase 4 Illustration"
								width={400}
								height={100}
								className="w-full h-auto rounded-lg shadow"
							/>
						)}
					</div>
				</div>

				{/* AI-Powered Insights */}
				<div className="font-semibold mb-2">AI-Powered Insights</div>
				<div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
					<img
						src="/menstruation-illustration.png"
						alt="Woman sitting illustration"
						className="w-full h-40 object-cover"
					/>
				</div>

				{/* Your Stats */}
				<div className="flex gap-6 mb-6">
					<div className="flex-1 bg-white rounded-lg shadow p-4">
						<div className="text-sm text-gray-500">Mood</div>
						<div className="text-xl font-semibold text-gray-700">Neutral</div>
					</div>
					<div className="flex-1 bg-white rounded-lg shadow p-4">
						<div className="text-sm text-gray-500">Temperature</div>
						<div className="text-xl font-semibold text-gray-700">98.6°F</div>
					</div>
				</div>

				{/* Estimated Period */}
				<div className="text-sm text-gray-500 mb-1">Estimated Period</div>
				<div className="font-medium text-gray-700">Jul 25 - Jul 29</div>
			</main>
		</div>
	);
};

export default DayOverview;
