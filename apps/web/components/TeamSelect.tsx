'use client';

import { useEffect, useRef, useState } from 'react';
import { ChevronDown, Search, Check } from 'lucide-react';
import { teams, getTeamLogo, type Team } from '@/lib/teams';
import Logo from './Logo';

interface TeamSelectProps {
    label: string;
    value: string;
    onChange: (name: string) => void;
    excludeTeam?: string;
}

export default function TeamSelect({ label, value, onChange, excludeTeam }: TeamSelectProps) {
    const [open, setOpen] = useState(false);
    const [query, setQuery] = useState('');
    const wrapperRef = useRef<HTMLDivElement>(null);
    const searchRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
                setOpen(false);
                setQuery('');
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        if (open) searchRef.current?.focus();
    }, [open]);

    const filtered: Team[] = teams.filter(
        (t) => t.name !== excludeTeam && t.name.toLowerCase().includes(query.toLowerCase())
    );

    const handleSelect = (name: string) => {
        onChange(name);
        setOpen(false);
        setQuery('');
    };

    return (
        <div ref={wrapperRef} className="relative">
            <label className="mb-1 block text-xs font-medium text-slate-400">{label}</label>

            <button
                type="button"
                onClick={() => setOpen(!open)}
                className="flex w-full items-center gap-3 rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-sm text-white transition-colors hover:border-slate-700 focus:border-blue-500 focus:outline-none"
            >
                <Logo src={getTeamLogo(value)} alt={value} size={22} />
                <span className="flex-1 truncate text-left">{value || 'Pilih tim...'}</span>
                <ChevronDown size={16} className={`text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>

            {open && (
                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-2xl shadow-black/40">
                    <div className="flex items-center gap-2 border-b border-slate-800 px-3 py-2">
                        <Search size={14} className="text-slate-500" />
                        <input
                            ref={searchRef}
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Cari tim..."
                            className="w-full bg-transparent text-sm text-white placeholder:text-slate-600 focus:outline-none"
                        />
                    </div>

                    <div className="max-h-64 overflow-y-auto py-1">
                        {filtered.length === 0 && (
                            <p className="px-3 py-3 text-center text-xs text-slate-500">Tim tidak ditemukan.</p>
                        )}
                        {filtered.map((team) => (
                            <button
                                key={team.name}
                                type="button"
                                onClick={() => handleSelect(team.name)}
                                className="flex w-full items-center gap-3 px-3 py-2.5 text-left text-sm text-slate-200 transition-colors hover:bg-slate-800/70"
                            >
                                <Logo src={team.logo} alt={team.name} size={22} />
                                <span className="flex-1 truncate">{team.name}</span>
                                {team.name === value && <Check size={15} className="text-blue-400" />}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}