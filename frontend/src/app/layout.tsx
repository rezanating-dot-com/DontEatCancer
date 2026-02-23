import type { Metadata } from "next";

import NavBar from "@/components/NavBar";

import "./globals.css";

export const metadata: Metadata = {
  title: "DontEatCancer",
  description: "Research repository for food chemical safety evidence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 antialiased">
        <NavBar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
