import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const sundry = localFont({
  src: [
    {
      path: "../public/boostai/fonts/sundry-variable.woff2",
      weight: "100 900",
      style: "normal"
    },
    {
      path: "../public/boostai/fonts/sundry-regular.woff2",
      weight: "400",
      style: "normal"
    }
  ],
  variable: "--font-sundry",
  display: "swap",
  preload: true
});

export const metadata: Metadata = {
  metadataBase: new URL("https://boostai.study"),
  title: {
    default: "BoostAI Study",
    template: "%s | BoostAI Study"
  },
  description:
    "Complete React source for the BoostAI landing experience, including the home, school, and university entry pages.",
  openGraph: {
    title: "BoostAI Study",
    description:
      "A three-page React landing experience for school and university students.",
    url: "https://boostai.study",
    siteName: "BoostAI Study",
    type: "website"
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={sundry.variable}>{children}</body>
    </html>
  );
}
