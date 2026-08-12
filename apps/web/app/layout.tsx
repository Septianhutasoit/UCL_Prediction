'use client';

import './globals.css';
import { useState } from 'react';
import { motion } from 'framer-motion';
import Sidebar from '@/components/Sidebar';
import Footer from '@/components/Footer';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <html lang="en" className="dark">
      <head>
        <title>ChampIntel - UCL AI Match Analysis</title>
        <meta
          name="description"
          content="AI-Powered UEFA Champions League Match Prediction & Analysis Platform"
        />
        <link rel="icon" href="/icon.png" type="image/png" />
      </head>
      <body className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-500 selection:text-white overflow-x-hidden">

        {/* Panggil Komponen Sidebar yang Modular */}
        <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

        {/* Main Content Area */}
        <motion.main
          animate={{ marginLeft: collapsed ? 72 : 240 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="min-h-screen flex-1 p-6 md:p-10 bg-slate-950 overflow-x-hidden w-full flex flex-col justify-between"
        >
          <div>
          {children}
          </div>
          <Footer />
        </motion.main>

      </body>
    </html>
  );
}