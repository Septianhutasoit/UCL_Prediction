'use client';

import Image from 'next/image';
import { useRef, useState, useEffect, useCallback } from 'react';
import { Volume2, VolumeX, ChevronLeft, ChevronRight } from 'lucide-react';

const leagues = [
    { name: 'Premier League', img: '/leagueucl/premier.png' },
    { name: 'La Liga', img: '/leagueucl/laliga.png' },
    { name: 'Serie A', img: '/leagueucl/serieA.png' },
    { name: 'Bundesliga', img: '/leagueucl/bundesliga.png' },
    { name: 'Ligue 1', img: '/leagueucl/ligue1.png' },
    { name: 'Eredivisie', img: '/leagueucl/eredevisie.png' },
    { name: 'Liga Portugal', img: '/leagueucl/portugal.png' },
];

const marqueeLeagues = [...leagues, ...leagues];

/**
 * Slide pertama = video intro, sisanya foto sejarah.
 * "title" & "description" ini masih placeholder — ganti dengan fakta asli
 * sesuai isi tiap foto di public/sejarah/.
 */
type HistorySlide = {
    type: 'video' | 'image';
    src: string;
    year?: string;
    title: string;
    description: string;
};

const historySlides: HistorySlide[] = [
    {
        type: 'video',
        src: '/videos/introucl.mp4',
        title: 'Anthem Resmi Liga Champions',
        description:
            'Lagu kebangsaan ikonik yang berkumandang di setiap stadion sebelum laga dimulai — simbol kebesaran dan sejarah panjang turnamen klub paling bergengsi di Eropa.',
    },
    {
        type: 'image',
        src: '/sejarah/rma.png',
        year: '15x Juara',
        title: 'Real Madrid — Sang Raja Eropa',
        description:
            'Pemegang rekor gelar terbanyak sepanjang sejarah kompetisi. Dominasi Real Madrid di ajang ini menjadikan mereka klub paling ditakuti di setiap fase gugur.',
    },
    {
        type: 'image',
        src: '/sejarah/15.png',
        year: 'Rekor',
        title: 'Rekor & Pencapaian Bersejarah',
        description:
            'Sepanjang perjalanannya, turnamen ini mencatat berbagai rekor individu maupun tim yang menjadi tolok ukur kehebatan sepak bola Eropa dari generasi ke generasi.',
    },
    {
        type: 'image',
        src: '/sejarah/2.png',
        year: 'Momen Ikonik',
        title: 'Momen-Momen Tak Terlupakan',
        description:
            'Dari comeback dramatis hingga gol-gol penentu di final, Liga Champions selalu menghadirkan momen yang dikenang jutaan penggemar sepak bola di seluruh dunia.',
    },
];

export default function UCLInfoPage() {
    /* ---------- Hero atmosphere video ---------- */
    const videoRef = useRef<HTMLVideoElement>(null);
    const [muted, setMuted] = useState(true);

    const toggleSound = () => {
        if (!videoRef.current) return;
        videoRef.current.muted = !videoRef.current.muted;
        setMuted(videoRef.current.muted);
    };

    /* ---------- History carousel ---------- */
    const trackRef = useRef<HTMLDivElement>(null);
    const introRef = useRef<HTMLVideoElement>(null);
    const [activeSlide, setActiveSlide] = useState(0);
    const [introMuted, setIntroMuted] = useState(true);

    const goToSlide = useCallback((index: number) => {
        const track = trackRef.current;
        if (!track) return;
        const clamped = Math.max(0, Math.min(index, historySlides.length - 1));
        track.scrollTo({ left: clamped * track.clientWidth, behavior: 'smooth' });
        setActiveSlide(clamped);
    }, []);

    const handleTrackScroll = () => {
        const track = trackRef.current;
        if (!track) return;
        const index = Math.round(track.scrollLeft / track.clientWidth);
        setActiveSlide(index);
    };

    const toggleIntroSound = () => {
        if (!introRef.current) return;
        introRef.current.muted = !introRef.current.muted;
        setIntroMuted(introRef.current.muted);
    };

    useEffect(() => {
        if (activeSlide !== 0 && introRef.current) {
            introRef.current.muted = true;
            setIntroMuted(true);
        }
    }, [activeSlide]);

    const current = historySlides[activeSlide];

    return (
        <div className="mx-auto max-w-6xl space-y-14 overflow-x-hidden">
            {/* Header */}
            <div className="flex items-start gap-5">
                <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-2xl shadow-lg shadow-blue-500/20 md:h-20 md:w-20">
                    <Image src="/icon.png" alt="UEFA Champions League" fill className="object-cover" />
                </div>
                <div className="max-w-2xl">
                    <span className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                        Tournament Overview
                    </span>
                    <h1 className="mt-1 text-4xl font-extrabold tracking-tight text-white md:text-5xl">
                        UEFA Champions League
                    </h1>
                    <p className="mt-3 text-slate-400">
                        Informasi resmi turnamen elit Eropa, format kompetisi baru, dan peta kekuatan liga peserta.
                    </p>
                </div>
            </div>

            {/* 1. Hero Video Atmosphere — sekarang paling atas */}
            <div className="relative w-full overflow-hidden rounded-[2rem] border border-slate-800 shadow-[0_20px_60px_-15px_rgba(37,99,235,0.35)]">
                <video
                    ref={videoRef}
                    autoPlay
                    loop
                    muted
                    playsInline
                    preload="auto"
                    className="h-[70vh] max-h-[560px] w-full object-cover"
                >
                    <source src="/videos/ucl.mp4" type="video/mp4" />
                    Browser Anda tidak mendukung tag video.
                </video>

                <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/10 to-transparent" />
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-slate-950/60 via-transparent to-transparent" />

                <button
                    onClick={toggleSound}
                    aria-label={muted ? 'Aktifkan suara' : 'Matikan suara'}
                    className="absolute right-5 top-5 z-10 flex h-10 w-10 items-center justify-center rounded-full border border-white/20 bg-black/50 text-white backdrop-blur-md transition-all hover:scale-105 hover:bg-black/80"
                >
                    {muted ? <VolumeX size={17} /> : <Volume2 size={17} />}
                </button>

                <div className="pointer-events-none absolute inset-x-0 bottom-0 flex flex-col gap-3 p-8 md:p-10">
                    <span className="w-fit rounded-full bg-blue-600/90 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white shadow-md backdrop-blur">
                        Official Atmosphere
                    </span>
                    <h3 className="max-w-lg text-2xl font-bold leading-tight text-white md:text-3xl">
                        The Stage of European Champions
                    </h3>
                </div>
            </div>

            {/* 2. Sejarah & Warisan Juara — carousel + panel penjelasan rapi */}
            <div className="space-y-5">
                <h2 className="text-xl font-semibold text-slate-200">Sejarah &amp; Warisan Juara</h2>

                <div className="grid grid-cols-1 gap-5 lg:grid-cols-5">
                    {/* Carousel visual */}
                    <div className="relative w-full overflow-hidden rounded-[2rem] border border-slate-800 shadow-[0_20px_60px_-15px_rgba(37,99,235,0.35)] lg:col-span-3">
                        <div
                            ref={trackRef}
                            onScroll={handleTrackScroll}
                            className="flex snap-x snap-mandatory overflow-x-auto scroll-smooth [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
                        >
                            {historySlides.map((slide, i) => (
                                <div key={i} className="relative h-[420px] w-full shrink-0 snap-center md:h-[480px]">
                                    {slide.type === 'video' ? (
                                        <video
                                            ref={introRef}
                                            autoPlay
                                            loop
                                            muted
                                            playsInline
                                            preload="auto"
                                            className="h-full w-full object-cover"
                                        >
                                            <source src={slide.src} type="video/mp4" />
                                        </video>
                                    ) : (
                                        <Image src={slide.src} alt={slide.title} fill className="object-cover" />
                                    )}
                                    <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
                                </div>
                            ))}
                        </div>

                        {activeSlide === 0 && (
                            <button
                                onClick={toggleIntroSound}
                                aria-label={introMuted ? 'Aktifkan suara' : 'Matikan suara'}
                                className="absolute right-5 top-5 z-10 flex h-10 w-10 items-center justify-center rounded-full border border-white/20 bg-black/50 text-white backdrop-blur-md transition-all hover:scale-105 hover:bg-black/80"
                            >
                                {introMuted ? <VolumeX size={17} /> : <Volume2 size={17} />}
                            </button>
                        )}

                        <button
                            onClick={() => goToSlide(activeSlide - 1)}
                            disabled={activeSlide === 0}
                            aria-label="Sebelumnya"
                            className="absolute left-4 top-1/2 z-10 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full border border-white/20 bg-black/40 text-white backdrop-blur-md transition-all hover:bg-black/70 disabled:pointer-events-none disabled:opacity-0"
                        >
                            <ChevronLeft size={18} />
                        </button>
                        <button
                            onClick={() => goToSlide(activeSlide + 1)}
                            disabled={activeSlide === historySlides.length - 1}
                            aria-label="Berikutnya"
                            className="absolute right-4 top-1/2 z-10 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full border border-white/20 bg-black/40 text-white backdrop-blur-md transition-all hover:bg-black/70 disabled:pointer-events-none disabled:opacity-0"
                        >
                            <ChevronRight size={18} />
                        </button>

                        <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 gap-1.5">
                            {historySlides.map((_, i) => (
                                <button
                                    key={i}
                                    onClick={() => goToSlide(i)}
                                    aria-label={`Slide ${i + 1}`}
                                    className={`h-1.5 rounded-full transition-all ${i === activeSlide ? 'w-6 bg-blue-400' : 'w-1.5 bg-white/40 hover:bg-white/60'
                                        }`}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Panel penjelasan — sinkron dengan slide aktif */}
                    <div className="flex flex-col justify-center rounded-[2rem] border border-slate-800 bg-slate-900/60 p-8 lg:col-span-2">
                        <div className="flex items-center gap-3">
                            <span className="text-xs font-bold text-blue-400">
                                {String(activeSlide + 1).padStart(2, '0')} / {String(historySlides.length).padStart(2, '0')}
                            </span>
                            {current.year && (
                                <span className="rounded-full border border-blue-500/30 bg-blue-500/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-blue-300">
                                    {current.year}
                                </span>
                            )}
                        </div>
                        <h3 className="mt-3 text-xl font-bold text-white md:text-2xl">{current.title}</h3>
                        <p className="mt-3 text-sm leading-relaxed text-slate-400">{current.description}</p>

                        <div className="mt-6 flex gap-2">
                            {historySlides.map((_, i) => (
                                <button
                                    key={i}
                                    onClick={() => goToSlide(i)}
                                    className={`h-1 flex-1 rounded-full transition-all ${i === activeSlide ? 'bg-blue-400' : 'bg-slate-700 hover:bg-slate-600'
                                        }`}
                                    aria-label={`Ke slide ${i + 1}`}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Format Swiss-Model */}
            <div className="flex flex-col gap-4 border-l-2 border-blue-500/60 pl-6 md:flex-row md:items-start md:gap-10">
                <h2 className="shrink-0 text-xl font-semibold text-blue-400 md:w-64">
                    Format Baru Kompetisi
                    <span className="mt-1 block text-sm font-normal text-slate-500">Swiss-Model</span>
                </h2>
                <p className="text-sm leading-relaxed text-slate-300">
                    Mulai musim ini, format tradisional babak grup dengan 32 tim resmi bertransformasi menjadi Fase Liga
                    (League Phase) tunggal beranggotakan 36 tim. Setiap klub akan memainkan 8 pertandingan melawan 8 lawan
                    berbeda (4 kandang, 4 tandang). Delapan tim teratas otomatis lolos ke babak 16 besar, sementara peringkat 9
                    hingga 24 akan bertarung di babak play-off.
                </p>
            </div>

            {/* Liga Peserta (Marquee) */}
            <div className="space-y-5">
                <h2 className="text-xl font-semibold text-slate-200">Asal Liga Klub Elite Peserta</h2>

                <div className="league-marquee group relative w-full overflow-hidden py-4">
                    <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-slate-950 to-transparent md:w-28" />
                    <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-slate-950 to-transparent md:w-28" />

                    <div className="league-marquee-track flex w-max items-center gap-16 group-hover:[animation-play-state:paused]">
                        {marqueeLeagues.map((league, i) => (
                            <div
                                key={`${league.name}-${i}`}
                                className="flex shrink-0 flex-col items-center gap-2 opacity-85 transition-opacity duration-300 hover:opacity-100"
                            >
                                <div className="relative h-12 w-12 md:h-14 md:w-14">
                                    <Image src={league.img} alt={league.name} fill className="object-contain" />
                                </div>
                                <span className="text-[11px] font-medium text-slate-500">{league.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <style>{`
        .league-marquee-track {
          animation: league-marquee-scroll 28s linear infinite;
        }
        @keyframes league-marquee-scroll {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
      `}</style>
        </div>
    );
}