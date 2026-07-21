import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Snip — URL Shortener",
  description: "Create short links, redirect visitors, and track click counts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
