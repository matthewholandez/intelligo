import type { Metadata } from "next";
import { EB_Garamond, Cormorant_Garamond, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Bookshelf } from "@/components/Bookshelf";
import { Footer } from "@/components/Footer";

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-eb-garamond",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-cormorant",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Intelligo",
  description: "A reading room that happens to translate.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${ebGaramond.variable} ${cormorant.variable} ${jetbrains.variable}`}
    >
      <body>
        <div className="app">
          <Bookshelf />
          <main>
            {children}
            <Footer />
          </main>
        </div>
      </body>
    </html>
  );
}
