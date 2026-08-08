import './globals.css';
import Link from 'next/link';

export const metadata = {
  title: 'ChampIntel - UCL AI Match Analysis',
  description: 'AI-Powered UEFA Champions League Match Prediction & Analysis Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 flex min-h-screen">

        {/* Sidebar Navigation (Samping Kiri) */}
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col fixed inset-y-0 z-50">

          {/* Logo / Brand */}
          <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
            <span className="text-xl font-extrabold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
              ⚽ ChampIntel AI
            </span>
          </div>

          {/* Menu Navigasi */}
          <nav className="flex-1 p-4 space-y-2">
            <Link
              href="/"
              className="flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <span>📊 Match Predictor</span>
            </Link>

            <Link
              href="/predictions"
              className="flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <span>🎯 Live Analysis</span>
            </Link>

            <Link
              href="/history"
              className="flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <span>📜 Prediction History</span>
            </Link>
          </nav>

          {/* Footer Sidebar */}
          <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
            ChampIntel v1.0 • UCL Engine
          </div>
        </aside>

        {/* Main Content Area (Kanan) */}
        <main className="flex-1 ml-64 p-10 bg-slate-950 min-h-screen">
          {children}
        </main>

      </body>
    </html>
  );
}