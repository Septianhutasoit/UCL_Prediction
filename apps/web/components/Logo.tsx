'use client';

import Image from 'next/image';
import { useState } from 'react';

interface LogoProps {
    src?: string;
    alt: string;
    size?: number;
    className?: string;
}

export default function Logo({ src, alt, size = 24, className = '' }: LogoProps) {
    const [failed, setFailed] = useState(false);

    if (!src || failed) {
        return (
            <div
                className={`flex shrink-0 items-center justify-center rounded-full border border-slate-700 bg-slate-800/80 text-slate-500 ${className}`}
                style={{ width: size, height: size }}
                title={alt}
            >
                <span style={{ fontSize: size * 0.5 }}>⚽</span>
            </div>
        );
    }

    return (
        <div className={`relative shrink-0 ${className}`} style={{ width: size, height: size }}>
            <Image
                src={src}
                alt={alt}
                fill
                sizes={`${size}px`}
                className="object-contain"
                onError={() => setFailed(true)}
            />
        </div>
    );
}