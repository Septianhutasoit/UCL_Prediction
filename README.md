<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChampIntel AI — UCL Prediction</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }

        .container {
            max-width: 1100px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 3rem 2.5rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
        }

        /* ========== HEADER ========== */
        .header {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .ucl-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            background: linear-gradient(135deg, #4a1a7a, #6C2BD9);
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #fff;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ucl-badge img {
            width: 28px;
            height: 28px;
        }

        .header h1 {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline-flex;
            align-items: center;
            gap: 1rem;
        }

        .header h1 img {
            width: 56px;
            height: 56px;
            -webkit-text-fill-color: initial;
        }

        .header .subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 0.25rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }

        .header .tagline {
            font-size: 1.5rem;
            font-weight: 600;
            background: linear-gradient(135deg, #c084fc, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-top: 0.5rem;
        }

        /* ========== BADGES ========== */
        .badge-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.75rem;
            margin: 1.5rem 0;
        }

        .badge {
            padding: 0.4rem 1.2rem;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(4px);
            transition: all 0.3s ease;
        }

        .badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(108, 43, 217, 0.3);
        }

        .badge.gold { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #1a1a2e; border: none; }
        .badge.green { background: linear-gradient(135deg, #34d399, #059669); color: #fff; border: none; }
        .badge.purple { background: linear-gradient(135deg, #a78bfa, #7c3aed); color: #fff; border: none; }
        .badge.orange { background: linear-gradient(135deg, #fb923c, #ea580c); color: #fff; border: none; }

        /* ========== PREDICTION CARD ========== */
        .prediction-card {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 24px;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .match-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .match-teams {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .match-teams .vs {
            color: rgba(255, 255, 255, 0.3);
            font-weight: 400;
        }

        .match-badge {
            padding: 0.3rem 1rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: rgba(251, 191, 36, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.2);
        }

        /* ========== PROGRESS BARS ========== */
        .probability-section {
            margin: 1.5rem 0;
        }

        .prob-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }

        .prob-label {
            width: 90px;
            font-size: 0.9rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.7);
        }

        .prob-bar-bg {
            flex: 1;
            height: 12px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 50px;
            overflow: hidden;
            position: relative;
        }

        .prob-bar-fill {
            height: 100%;
            border-radius: 50px;
            transition: width 1.5s ease;
        }

        .prob-bar-fill.home { background: linear-gradient(90deg, #34d399, #059669); width: 58%; }
        .prob-bar-fill.draw { background: linear-gradient(90deg, #fbbf24, #f59e0b); width: 27%; }
        .prob-bar-fill.away { background: linear-gradient(90deg, #fb923c, #ea580c); width: 15%; }

        .prob-percent {
            width: 50px;
            text-align: right;
            font-weight: 700;
            font-size: 0.95rem;
            color: rgba(255, 255, 255, 0.9);
        }

        /* ========== SHAP ANALYSIS ========== */
        .shap-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .shap-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.6rem 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .shap-bar {
            flex: 1;
            height: 6px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 50px;
            overflow: hidden;
        }

        .shap-fill {
            height: 100%;
            border-radius: 50px;
            background: linear-gradient(90deg, #a78bfa, #818cf8);
        }

        .shap-label {
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.7);
            min-width: 100px;
        }

        .shap-value {
            font-weight: 700;
            font-size: 0.9rem;
            color: #a78bfa;
            min-width: 50px;
            text-align: right;
        }

        /* ========== AI NARRATIVE ========== */
        .narrative-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-left: 3px solid #a78bfa;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.7;
            font-size: 0.95rem;
        }

        .narrative-box strong {
            color: #c084fc;
        }

        /* ========== TABLE ========== */
        .table-wrap {
            overflow-x: auto;
            margin: 1.5rem 0;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th {
            background: rgba(255, 255, 255, 0.04);
            padding: 0.9rem 1rem;
            text-align: left;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.5px;
        }

        td {
            padding: 0.8rem 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            color: rgba(255, 255, 255, 0.8);
        }

        .badge-small {
            padding: 0.2rem 0.8rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-small.green { background: rgba(52, 211, 153, 0.15); color: #34d399; }
        .badge-small.orange { background: rgba(251, 146, 60, 0.15); color: #fb923c; }
        .badge-small.purple { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }

        /* ========== FOOTER ========== */
        .footer {
            text-align: center;
            margin-top: 2.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            color: rgba(255, 255, 255, 0.3);
            font-size: 0.8rem;
            letter-spacing: 0.3px;
        }

        .footer a {
            color: #a78bfa;
            text-decoration: none;
        }

        /* ========== RESPONSIVE ========== */
        @media (max-width: 768px) {
            .container { padding: 1.5rem; }
            .header h1 { font-size: 2.2rem; flex-wrap: wrap; justify-content: center; }
            .header h1 img { width: 40px; height: 40px; }
            .match-teams { font-size: 1.2rem; gap: 0.75rem; }
            .shap-grid { grid-template-columns: 1fr; }
            .badge-row { gap: 0.5rem; }
            .prob-label { width: 70px; font-size: 0.8rem; }
        }

        @media (max-width: 480px) {
            .header h1 { font-size: 1.6rem; }
            .match-teams { font-size: 1rem; flex-wrap: wrap; justify-content: center; }
            .match-header { flex-direction: column; align-items: center; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">

        <!-- ==================== HEADER ==================== -->
        <div class="header">
            <div class="ucl-badge">
                <img src="https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/UEFA_Champions_League_logo.svg/800px-UEFA_Champions_League_logo.svg.png" alt="UCL" />
                UEFA Champions League 2025/26
            </div>

            <h1>
                <img src="https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/UEFA_Champions_League_logo.svg/800px-UEFA_Champions_League_logo.svg.png" alt="UCL" />
                ChampIntel AI
                <img src="https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/UEFA_Champions_League_logo.svg/800px-UEFA_Champions_League_logo.svg.png" alt="UCL" />
            </h1>
            <p class="subtitle">⚡ AI-Powered Match Prediction • Leg 1 → Leg 2 → Wembley</p>
            <p class="tagline">Where Data Meets Football Intelligence</p>
        </div>

        <!-- ==================== BADGES ==================== -->
        <div class="badge-row">
            <span class="badge gold">🏆 UCL Knockout</span>
            <span class="badge green">📊 Accuracy 84%</span>
            <span class="badge purple">🧠 SHAP Explained</span>
            <span class="badge orange">🤖 Qwen 2.5</span>
            <span class="badge">Leg 1 ✅</span>
            <span class="badge gold">Leg 2 🔥</span>
            <span class="badge">Wembley ⏳</span>
        </div>

        <!-- ==================== PREDICTION CARD ==================== -->
        <div class="prediction-card">
            <div class="match-header">
                <div class="match-teams">
                    <span>⚪ Real Madrid</span>
                    <span class="vs">vs</span>
                    <span>🔴 Bayern Munich</span>
                </div>
                <span class="match-badge">🏆 Quarter-Final • Leg 2</span>
            </div>

            <div class="probability-section">
                <div class="prob-item">
                    <span class="prob-label">🏠 Home Win</span>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill home"></div>
                    </div>
                    <span class="prob-percent">58%</span>
                </div>
                <div class="prob-item">
                    <span class="prob-label">🤝 Draw</span>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill draw"></div>
                    </div>
                    <span class="prob-percent">27%</span>
                </div>
                <div class="prob-item">
                    <span class="prob-label">✈️ Away Win</span>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill away"></div>
                    </div>
                    <span class="prob-percent">15%</span>
                </div>
            </div>

            <!-- ========== SHAP ANALYSIS ========== -->
            <div style="margin-top: 1.5rem;">
                <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">🔍 SHAP Analysis — Key Factors</p>
                <div class="shap-grid">
                    <div class="shap-item">
                        <span class="shap-label">🏠 Home Advantage</span>
                        <div class="shap-bar"><div class="shap-fill" style="width: 75%;"></div></div>
                        <span class="shap-value">+15%</span>
                    </div>
                    <div class="shap-item">
                        <span class="shap-label">⚽ Attacking Efficiency</span>
                        <div class="shap-bar"><div class="shap-fill" style="width: 60%;"></div></div>
                        <span class="shap-value">+12%</span>
                    </div>
                    <div class="shap-item">
                        <span class="shap-label">🔥 Last 5 Form</span>
                        <div class="shap-bar"><div class="shap-fill" style="width: 40%;"></div></div>
                        <span class="shap-value">+8%</span>
                    </div>
                    <div class="shap-item">
                        <span class="shap-label">🤝 H2H Record</span>
                        <div class="shap-bar"><div class="shap-fill" style="width: 35%;"></div></div>
                        <span class="shap-value">+7%</span>
                    </div>
                    <div class="shap-item" style="grid-column: 1 / -1;">
                        <span class="shap-label">⚡ Leg 1 Aggregate</span>
                        <div class="shap-bar"><div class="shap-fill" style="width: 25%;"></div></div>
                        <span class="shap-value">+5%</span>
                    </div>
                </div>
            </div>

            <!-- ========== AI NARRATIVE ========== -->
            <div class="narrative-box">
                <strong>🧠 AI Analysis:</strong> Real Madrid holds a commanding <strong>58%</strong> probability of winning this Leg 2 clash. The SHAP analysis reveals that <strong>home advantage</strong> is the most decisive factor (+15%), followed by their superior <strong>attacking efficiency</strong> (+12%). With a <strong>2-1 aggregate lead</strong> from Leg 1, Madrid can afford a defensive approach while Bayern must chase an early goal to overturn the deficit.
            </div>

            <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem;">
                <span style="padding: 0.4rem 1.2rem; background: rgba(52, 211, 153, 0.1); border-radius: 50px; border: 1px solid rgba(52, 211, 153, 0.2); color: #34d399; font-size: 0.85rem;">🔮 Predicted Score: 2-1</span>
                <span style="padding: 0.4rem 1.2rem; background: rgba(167, 139, 250, 0.1); border-radius: 50px; border: 1px solid rgba(167, 139, 250, 0.2); color: #a78bfa; font-size: 0.85rem;">📊 Confidence: 74%</span>
            </div>
        </div>

        <!-- ==================== TABLE ==================== -->
        <div style="margin: 2rem 0;">
            <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">📊 Featured Matches This Week</p>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Match</th>
                            <th>Venue</th>
                            <th>Prediction</th>
                            <th>Confidence</th>
                            <th>Key Factor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Real Madrid</strong> vs Bayern Munich</td>
                            <td>Bernabéu</td>
                            <td><span class="badge-small green">🏠 Home Win</span></td>
                            <td>74%</td>
                            <td>Home Advantage</td>
                        </tr>
                        <tr>
                            <td><strong>Liverpool</strong> vs Barcelona</td>
                            <td>Anfield</td>
                            <td><span class="badge-small green">🏠 Home Win</span></td>
                            <td>71%</td>
                            <td>Anfield Atmosphere</td>
                        </tr>
                        <tr>
                            <td>PSG vs <strong>Man City</strong></td>
                            <td>Parc des Princes</td>
                            <td><span class="badge-small purple">✈️ Away Win</span></td>
                            <td>68%</td>
                            <td>Away Form</td>
                        </tr>
                        <tr>
                            <td>Inter vs <strong>Arsenal</strong></td>
                            <td>San Siro</td>
                            <td><span class="badge-small purple">✈️ Away Win</span></td>
                            <td>65%</td>
                            <td>Set Pieces</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ==================== FOOTER ==================== -->
        <div class="footer">
            ⚽ ChampIntel AI — Where Data Meets Football Intelligence &nbsp;•&nbsp; 🏆 UCL 2025/26
            <br>
            <a href="#">⬆ Back to Top</a>
        </div>

    </div>
</body>
</html>
