import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

const footerLinks = [
    { href: '/', label: 'Match Predictor' },
    { href: '/predictions', label: 'Live Analysis' },
    { href: '/ucl-info', label: 'UCL Information' },
    { href: '/history', label: 'Prediction History' },
];

const partnerLogos = [
    '/sponsor/uefa.png',
    '/sponsor/adidas.png',
    '/sponsor/all.png',
    '/sponsor/easports.png',
    '/sponsor/axa.png',
    '/sponsor/fedex.png',
    '/sponsor/standard.png',
    '/sponsor/t.png',
    '/sponsor/nike.png'
];

export default function Footer() {
    return (
        <footer
            className="mt-20 border border-slate-800/80 py-10 px-6 rounded-3xl backdrop-blur-md bg-cover bg-center relative overflow-hidden shadow-2xl"
            style={{
                backgroundImage: `linear-gradient(to bottom, rgba(2, 6, 23, 0.88), rgba(2, 6, 23, 0.96)), url('/UCL.jpg')`
            }}
        >
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 relative z-10">

                {/* Brand & Deskripsi */}
                <div className="flex flex-col items-center md:items-start space-y-3">
                    <div className="flex items-center space-x-3">
                        <div className="relative h-9 w-9 shrink-0 overflow-hidden rounded-xl shadow-md border border-slate-800/60">
                            <Image src="/icon.png" alt="ChampIntel Logo" fill className="object-cover" />
                        </div>
                        <span className="font-extrabold text-sm bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                            ChampIntel AI
                        </span>
                    </div>
                    <p className="text-xs text-slate-400 text-center md:text-left max-w-xs">
                        Platform Prediksi & Analisis Taktik UEFA Champions League berbasis Machine Learning XGBoost.
                    </p>
                </div>

                {/* Quick Links */}
                <div className="flex flex-wrap justify-center gap-6 text-xs font-semibold text-slate-300">
                    {footerLinks.map((link) => (
                        <Link key={link.href} href={link.href} className="hover:text-blue-400 transition-colors">
                            {link.label}
                        </Link>
                    ))}
                </div>

                {/* Logo Sponsor (Polos, Lebih Besar, Tanpa Kotak) */}
                <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6 opacity-75 hover:opacity-100 transition-opacity max-w-md">
                    {partnerLogos.map((src, i) => (
                        <div key={i} className="h-7 w-11 relative transition-transform duration-300 hover:scale-110">
                            <Image src={src} alt="Sponsor Logo" fill className="object-contain drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]" />
                        </div>
                    ))}
                </div>

            </div>

            {/* Copyright */}
            <div className="max-w-7xl mx-auto mt-8 pt-6 border-t border-slate-800/40 text-center text-[10px] text-slate-500 relative z-10">
                © {new Date().getFullYear()} ChampIntel. All rights reserved. Built with Next.js, Go (Gin), FastAPI, & XGBoost.
            </div>
        </footer>
    );
}