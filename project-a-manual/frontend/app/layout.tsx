import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Notes",
  description: "A small notes app backed by the Notes API. Written by Daniel Osi.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
