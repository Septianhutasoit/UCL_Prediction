'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
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

export default function Sidebar({ collapsed, setCollapsed }: { collapsed: boolean; setCollapsed: (val: boolean) => void }) {
    const pathname = usePathname();

    return (
        <motion.aside
            animate={{ width: collapsed ? 72 : 240 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed inset-y-0 z-50 flex flex-col border-r border-slate-800/80 bg-slate-900/90 shadow-2xl backdrop-blur-xl overflow-hidden"
        >
            {/* Header: Logo & Tombol Toggle */}
            <div className={`flex items-center p-3.5 border-b border-slate-800/80 ${collapsed ? 'flex-col gap-3' : 'justify-between'}`}>
                <div className="flex items-center space-x-2.5">
                    <div className="relative h-9 w-9 shrink-0 overflow-hidden rounded-xl shadow-md border border-slate-800/60">
                        <Image src="/icon.png" alt="ChampIntel Logo" fill className="object-cover" />
                    </div>
                    <AnimatePresence initial={false}>
                        {!collapsed && (
                            <motion.span
                                initial={{ opacity: 0, width: 0 }}
                                animate={{ opacity: 1, width: 'auto' }}
                                exit={{ opacity: 0, width: 0 }}
                                transition={{ duration: 0.15 }}
                                className="font-bold text-sm bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent truncate"
                            >
                                ChampIntel
                            </motion.span>
                        )}
                    </AnimatePresence>
                </div>

                <button
                    onClick={() => setCollapsed(!collapsed)}
                    aria-label={collapsed ? 'Perbesar navbar' : 'Perkecil navbar'}
                    className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-800 bg-slate-800/60 text-slate-400 hover:text-blue-400 hover:border-blue-500/40 transition-colors cursor-pointer"
                >
                    {collapsed ? <PanelLeftOpen size={14} /> : <PanelLeftClose size={14} />}
                </button>
            </div>

            {/* Search */}
            <div className="p-3 pb-1">
                <div className={`flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-500 ${collapsed ? 'h-8 w-8 justify-center mx-auto' : 'h-8 px-2.5'}`}>
                    <Search size={14} />
                    {!collapsed && <span className="text-[11px]">Cari tim / laga...</span>}
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 space-y-1 p-3">
                {navItems.map(({ href, label, icon: Icon }) => {
                    const active = pathname === href;
                    return (
                        <Link
                            key={href}
                            href={href}
                            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-semibold transition-all ${collapsed ? 'justify-center' : ''
                                } ${active
                                    ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30 shadow-sm'
                                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent'
                                }`}
                        >
                            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${active ? 'bg-blue-500 text-white' : 'bg-slate-800/60 text-slate-400'}`}>
                                <Icon size={16} />
                            </span>
                            {!collapsed && <span className="truncate">{label}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="border-t border-slate-800/80 p-3 text-center text-[10px] text-slate-500 bg-slate-900/40">
                {!collapsed ? <p className="font-medium text-slate-400">ChampIntel v1.0</p> : <p>v1.0</p>}
            </div>
        </motion.aside>
    );
}