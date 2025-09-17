import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import StoreProvider from "./StoreProvider";
import NavigationBar from "./components/NavigationBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "WildChat Visualize",
  description: "WildChat Visualize",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <StoreProvider>
      <html lang="en">
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased` + ` overflow-hidden h-screen max-h-screen`}
        >
          <NavigationBar />
          <div className="flex flex-row overflow-hidden" style={{height: "95%"}}>
            {children}
          </div>
        </body>
      </html>
    </StoreProvider>
  );
}
