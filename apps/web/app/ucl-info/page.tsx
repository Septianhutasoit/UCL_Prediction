import Image from 'next/image';

const leagues = [
    { name: 'Premier League', img: '/leagueucl/premier.png' },
    { name: 'La Liga', img: '/leagueucl/laliga.png' },
    { name: 'Serie A', img: '/leagueucl/serieA.png' },
    { name: 'Bundesliga', img: '/leagueucl/bundesliga.png' },
    { name: 'Ligue 1', img: '/leagueucl/ligue1.png' },
    { name: 'Eredivisie', img: '/leagueucl/eredevisie.png' },
    { name: 'Liga Portugal', img: '/leagueucl/portugal.png' },
];

export default function UCLInfoPage() {
    return (
        <div className="max-w-5xl mx-auto space-y-10">

            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white">UEFA Champions League Overview</h1>
                <p className="text-slate-400 mt-1">
                    Informasi resmi turnamen elit Eropa, format kompetisi baru, dan peta kekuatan liga peserta.
                </p>
            </div>

            {/* Format Swiss-Model */}
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-xl space-y-4">
                <h2 className="text-xl font-semibold text-blue-400">Format Baru Kompetisi (Swiss-Model)</h2>
                <p className="text-slate-300 text-sm leading-relaxed">
                    Mulai musim ini, format tradisional babak grup dengan 32 tim resmi bertransformasi menjadi **Fase Liga (League Phase) tunggal beranggotakan 36 tim**. Setiap klub akan memainkan 8 pertandingan melawan 8 lawan berbeda (4 kandang, 4 tandang). Delapan tim teratas otomatis lolos ke babak 16 besar, sementara peringkat 9 hingga 24 akan bertarung di babak *play-off*.
                </p>
            </div>

            {/* Liga Peserta */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-200">Asal Liga Klub Elite Peserta</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {leagues.map((league) => (
                        <div
                            key={league.name}
                            className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col items-center justify-center space-y-3 hover:border-slate-700 transition-all shadow-lg"
                        >
                            <div className="w-14 h-14 relative">
                                <Image src={league.img} alt={league.name} fill className="object-contain" />
                            </div>
                            <span className="text-xs font-medium text-slate-300">{league.name}</span>
                        </div>
                    ))}
                </div>
            </div>

        </div>
    );
}