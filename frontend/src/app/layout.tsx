import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "DontEatCancer",
  description: "Research repository for food chemical safety evidence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 antialiased">
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link href="/" className="text-xl font-bold text-gray-900">
                DontEatCancer
              </Link>
              <div className="flex items-center gap-6">
                <Link href="/ingredients" className="text-sm text-gray-600 hover:text-gray-900">
                  Ingredients
                </Link>
                <Link href="/search" className="text-sm text-gray-600 hover:text-gray-900">
                  Search
                </Link>
                <Link href="/tools/query-generator" className="text-sm text-gray-600 hover:text-gray-900">
                  Query Generator
                </Link>
                <Link href="/tools/upload" className="text-sm text-gray-600 hover:text-gray-900">
                  Upload
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
