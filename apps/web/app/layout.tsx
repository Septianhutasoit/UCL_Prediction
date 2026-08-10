'use client';

import './globals.css';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trophy,
  Radar,
  Crosshair,
  ScrollText,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
} from 'lucide-react';

const navItems = [
  { href: '/ucl-info', label: 'UCL Information', icon: Trophy },
  { href: '/', label: 'Match Predictor', icon: Radar },
  { href: '/predictions', label: 'Live Analysis', icon: Crosshair },
  { href: '/history', label: 'Prediction History', icon: ScrollText },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <html lang="en" className="dark">
      <head>
        <title>ChampIntel - UCL AI Match Analysis</title>
        <meta
          name="description"
          content="AI-Powered UEFA Champions League Match Prediction & Analysis Platform"
        />
        {/* Memanggil ikon browser secara langsung agar pasti terpanggil */}
        <link rel="icon" href="/icon.png" type="image/png" />
      </head>
      <body className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-500 selection:text-white">
        
        {/* Sidebar */}
        <motion.aside
          animate={{ width: collapsed ? 76 : 248 }}
          transition={{ type: 'spring', stiffness: 280, damping: 30 }}
          className="fixed inset-y-0 z-50 flex flex-col overflow-hidden border-r border-slate-800/80 bg-slate-900/90 shadow-2xl backdrop-blur-xl"
        >
          {/* Header: logo + collapse toggle */}
          <div className={`flex items-center gap-2.5 p-4 ${collapsed ? 'flex-col' : 'justify-between'}`}>
            <div className={`flex items-center ${collapsed ? 'flex-col gap-2' : 'gap-2.5'}`}>
              <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-blue-500/30 bg-gradient-to-br from-blue-500/20 to-indigo-600/20 p-1.5">
                {/* Menggunakan width & height tetap untuk menghindari warning sizes */}
                <Image src="/icon.png" alt="ChampIntel Logo" width={22} height={22} className="object-contain" />
              </div>
              <AnimatePresence initial={false}>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: 0.15 }}
                    className="overflow-hidden whitespace-nowrap text-base font-black tracking-wide text-white"
                  >
                    ChampIntel
                  </motion.span>
                )}
              </AnimatePresence>
            </div>

            <button
              onClick={() => setCollapsed(!collapsed)}
              aria-label={collapsed ? 'Perbesar navbar' : 'Perkecil navbar'}
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-800 bg-slate-800/60 text-slate-400 transition-colors hover:border-blue-500/40 hover:text-blue-400 cursor-pointer"
            >
              {collapsed ? <PanelLeftOpen size={15} /> : <PanelLeftClose size={15} />}
            </button>
          </div>

          {/* Search */}
          <div className="px-3 pb-2">
            <div
              className={`flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-500 ${
                collapsed ? 'h-9 w-9 justify-center mx-auto' : 'h-9 px-3'
              }`}
            >
              <Search size={15} />
              {!collapsed && (
                <>
                  <span className="flex-1 text-xs">Cari tim / laga...</span>
                  <span className="rounded-md border border-slate-800 bg-slate-900 px-1.5 py-0.5 text-[10px] text-slate-600">
                    /
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Section label */}
          {!collapsed && (
            <div className="px-5 pb-1.5 pt-3 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
              Navigation
            </div>
          )}

          {/* Nav */}
          <nav className="flex-1 space-y-1 px-3 pt-1">
            {navItems.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`group relative flex items-center gap-3 rounded-xl px-2.5 py-2.5 text-[13px] font-medium transition-colors duration-200 ${
                    collapsed ? 'justify-center' : ''
                  } ${
                    active
                      ? 'bg-slate-800/80 text-white'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  }`}
                >
                  <span
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors ${
                      active ? 'bg-blue-500 text-white shadow-md shadow-blue-500/30' : 'bg-slate-800/60 text-slate-400'
                    }`}
                  >
                    <Icon size={16} strokeWidth={2.25} />
                  </span>

                  {!collapsed && <span className="truncate">{label}</span>}

                  {/* Tooltip shown only when collapsed, on hover */}
                  {collapsed && (
                    <span className="pointer-events-none absolute left-full ml-3 whitespace-nowrap rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white opacity-0 shadow-lg shadow-blue-600/30 transition-opacity duration-150 group-hover:opacity-100 z-50">
                      {label}
                      <span className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-blue-600" />
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div
            className={`border-t border-slate-800/80 p-4 text-center text-[10px] text-slate-600 ${
              collapsed ? 'px-1' : ''
            }`}
          >
            {!collapsed ? (
              <>
                <p className="font-medium text-slate-500">ChampIntel v1.0</p>
                <p className="mt-0.5">Powered by Go &amp; XGBoost</p>
              </>
            ) : (
              <p>v1.0</p>
            )}
          </div>
        </motion.aside>

        {/* Main content */}
        <motion.main
          animate={{ marginLeft: collapsed ? 76 : 248 }}
          transition={{ type: 'spring', stiffness: 280, damping: 30 }}
          className="min-h-screen flex-1 bg-slate-950 p-6 md:p-12"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </motion.main>
      </body>
    </html>
  );
}