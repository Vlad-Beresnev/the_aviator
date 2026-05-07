'use client';

import { useState } from 'react';

const ARCH_NODES = [
  {
    id: 'browser',
    label: 'Selain',
    logos: [{ src: '/logos/browser.svg', alt: 'Browser' }],
    desc: 'React + Phaser.js + React-Leaflet',
    details: [
      'Kolme päänäkymää: kartta (/map), peli (/game/[ident]), tulostaulukko (/leaderboard)',
      'Phaser.js renderöi pelimaailman suoraan canvas-elementtiin — ei React DOM -renderöintiä',
      'React-Leaflet näyttää 451 large_airport-markkeria klusteröituna — vain näkyvän alueen kentät haetaan kerrallaan',
      'JWT-tokeni tallennetaan localStorage:iin ja välitetään API-pyynöissä Bearer-otsikossa',
    ],
  },
  {
    id: 'vercel',
    label: 'Vercel / Next.js 16',
    logos: [
      { src: '/logos/vercel.svg', alt: 'Vercel' },
      { src: '/logos/nextjs.svg', alt: 'Next.js' },
    ],
    desc: 'Frontend hosting, reititys, auth-suojaus',
    details: [
      'App Router -arkkitehtuuri — reitit hakemistorakenteesta, ei erillistä reititintiedostoa',
      'proxy.ts suojaa /map ja /game/:path* — kirjautumaton käyttäjä ohjataan /login-sivulle',
      'Automaattinen deploy GitHub-puskauksen jälkeen — jokainen commit julkaistaan tuotantoon',
      'Staattinen esirendering + client-side hydraatio — sivut latautuvat nopeasti',
      'NEXT_PUBLIC_API_URL ympäristömuuttuja sitoo frontendin Render-backendiin buildausaikana',
    ],
  },
  {
    id: 'render',
    label: 'Render / FastAPI',
    logos: [
      { src: '/logos/render.png', alt: 'Render' },
      { src: '/logos/fastapi.svg', alt: 'FastAPI' },
    ],
    desc: 'REST API — autentikointi, pelitila, pisteet',
    details: [
      '8 päätepistettä: POST /auth/register, POST /auth/login, GET /airports, GET /airports/{ident}, POST /game/start, GET /game/state, POST /game/complete-level, GET /scores',
      'bcrypt-salasanahajautus rekisteröinnissä — selkokielisiä salasanoja ei tallenneta',
      'JWT-tokenin voimassaolo 7 päivää — token validoidaan joka suojatussa pyynnössä',
      'Free tier: palvelin nukkuu 15 min käyttämättömyyden jälkeen, herää ~30 sekunnissa',
      'CORS-sallitut lähteet asetetaan ALLOWED_ORIGINS-ympäristömuuttujalla',
    ],
  },
  {
    id: 'python',
    label: 'Python-pelilogiikka',
    logos: [{ src: '/logos/python.svg', alt: 'Python' }],
    desc: 'Alkuperäinen CLI-koodi säilytetty sellaisenaan',
    details: [
      '5 moduulia: airport_service.py, game_logic.py, db_manager.py, player_service.py, action_game.py',
      '~500 riviä toimivaa Python-koodia — ei kirjoitettu uudelleen TypeScriptiksi',
      'FastAPI importoi nämä moduulit suoraan ja kutsuu niiden funktioita',
      'Ainoa pakollinen uudelleenkirjoitus: Pygame → Phaser.js (Pygame ei toimi selaimessa)',
      'Tämä lähestymistapa säästää aikaa ja estää bugien uudelleenluomisen',
    ],
  },
  {
    id: 'aiven',
    label: 'Aiven / MySQL',
    logos: [
      { src: '/logos/aiven.svg', alt: 'Aiven' },
    ],
    desc: 'Pilvi-MySQL — 4 taulukkoa, 6 899 lentokenttää',
    details: [
      'Aiven ilmaistaso: 1 GB, Frankfurt EU Central -alue (sama kuin Render)',
      'SSL-yhteys pakollinen — mysql-connector-python ssl_disabled=False',
      '6 899 lentokenttää airport-taulussa — vain ~450 large_airport-tyyppiä on pelikenttiä',
      'run_migrations() ajetaan käynnistyksessä — luo puuttuvat taulukot ja sarakkeet automaattisesti',
      'Alkuperäinen kehitystietokanta: MariaDB (Mac) → tuotanto: MySQL (Aiven) — aiheutti yhteensopivuusongelmia',
    ],
  },
];

const DB_TABLES = [
  {
    name: 'airport',
    role: 'Kaikki 6 899 lentokenttää maailmasta',
    columns: [
      'id INT',
      'ident VARCHAR(40) PK',
      'name VARCHAR(40)',
      'type VARCHAR(40)',
      'latitude_deg DOUBLE',
      'longitude_deg DOUBLE',
      'continent VARCHAR(40)',
      'is_unlocked BOOLEAN',
    ],
    notes: 'Charset latin1 — pakollinen FK-yhteensopivuuden vuoksi game-taulun kanssa. is_unlocked lisättiin migraatiolla.',
  },
  {
    name: 'goal',
    role: 'Pelitavoitteet large_airport-kentille',
    columns: [
      'id INT PK',
      'airport_ident → airport',
      'target_minvalue INT',
      'target_maxvalue INT',
    ],
    notes: 'Vain large_airport-tyyppiset kentät saavat goal-rivin. Palkintosumma lasketaan ident-hajautusfunktiolla — deterministinen, ei satunnainen.',
  },
  {
    name: 'game',
    role: 'Pelaajan pelitila ja edistyminen',
    columns: [
      'id INT PK',
      'name VARCHAR(100)',
      'money INT',
      'battery_used DOUBLE',
      'global_awareness INT',
      'current_airport → airport',
      'user_id → users',
      'created_at TIMESTAMP',
    ],
    notes: 'created_at lisättiin vaiheessa 5 tulostaulukko-näkymää varten — vanhat rivit saivat migrointihetken aikaleiman. user_id nullable — CLI-pelien rivit eivät liity käyttäjään.',
  },
  {
    name: 'users',
    role: 'Web-sovelluksen käyttäjätilit',
    columns: [
      'id INT PK',
      'username VARCHAR(100) UNIQUE',
      'password_hash VARCHAR(255)',
      'created_at TIMESTAMP',
    ],
    notes: 'Salasana tallennetaan bcrypt-hajautettuna. Charset utf8mb4 — tukee erikoismerkkejä käyttäjänimessä.',
  },
];

const DB_INSIGHTS = [
  { icon: '🔄', title: 'Automaattiset migraatiot', desc: 'run_migrations() ajetaan joka käynnistyksessä. Funktio tarkistaa _column_exists()-apufunktiolla ennen ALTER TABLE -komentoa — idempotenttisuus eli turvallinen ajaa useasti.' },
  { icon: '⚠️', title: 'MariaDB → MySQL ongelma', desc: 'Kehityskoneella MariaDB, tuotannossa MySQL. MariaDB-spesifinen ADD COLUMN IF NOT EXISTS -syntaksi kaatoi sovelluksen käynnistyksessä — korjattu _column_exists()-tarkistuksella.' },
  { icon: '🔤', title: 'Charset-yhteensopivuus', desc: 'airport- ja game-taulut käyttävät latin1-merkistöä. Tämä johtuu siitä, että airport-taulu luotiin alun perin latin1:llä — FK-viittauksen sarakkeiden merkistöjen on täsmättävä.' },
  { icon: '📊', title: 'Datamäärä', desc: '6 899 lentokenttää, joista ~450 on large_airport-tyyppiä ja saa goal-rivin. Karttanäkymä hakee vain näkyvän alueen kentät hakuparametreilla (south, north, west, east).' },
];

const TECH_STACK = [
  { logo: '/logos/nextjs.svg', name: 'Next.js 16', desc: 'Frontend-framework, App Router, TypeScript' },
  { logo: '/logos/fastapi.svg', name: 'FastAPI', desc: 'Python REST API, uvicorn' },
  { logo: '/logos/phaser.png', name: 'Phaser.js', desc: 'Selainpelimootori, canvas-renderöinti' },
  { logo: '/logos/react-leaflet.svg', name: 'React-Leaflet', desc: 'Interaktiivinen kartta, 451 lentokenttää' },
  { logo: '/logos/mysql.svg', name: 'MySQL', desc: 'Relaatiotietokanta, Aiven-pilvipalvelu' },
  { logo: '/logos/python.svg', name: 'Python', desc: 'Alkuperäinen pelilogiikka säilytetty' },
  { logo: '/logos/vercel.svg', name: 'Vercel', desc: 'Frontend hosting, automaattinen deploy' },
  { logo: '/logos/render.png', name: 'Render', desc: 'Backend hosting, REST API' },
];

export default function AboutPage() {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [activeTable, setActiveTable] = useState<string | null>(null);

  return (
    <div className="bg-gray-950 text-white min-h-screen">
      <main className="max-w-5xl mx-auto px-6 py-16 space-y-24">

        {/* Section 1 — Hero */}
        <section className="text-center space-y-6 pt-8">
          <h1 className="text-5xl font-bold tracking-tight">✈ The Aviator</h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Opi lentäminen — lennä ympäri maailman, pidä luentoja ja nouse tulostaulukon kärkeen.
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a href="/map" className="rounded border border-white/30 px-6 py-2 text-sm font-medium hover:bg-white/10 transition-colors">
              Pelaa nyt →
            </a>
            <a href="/leaderboard" className="rounded border border-white/30 px-6 py-2 text-sm font-medium hover:bg-white/10 transition-colors">
              Tulostaulukko
            </a>
          </div>
        </section>

        {/* Section 2 — Ennen ja jälkeen */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Ennen ja jälkeen</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-start">
            <div>
              <p className="text-sm text-gray-400 mb-4 font-medium uppercase tracking-wide">Ennen — Komentorivi + Pygame</p>
              <div className="space-y-4">
                <img
                  src="/screenshots/cli-menu.png"
                  alt="CLI päävalikko — THE AVIATOR terminaalissa"
                  className="w-full rounded-xl border border-white/10 shadow-lg"
                />
                <img
                  src="/screenshots/cli-levels.png"
                  alt="CLI tasojen valinta — lentokenttälista terminaalissa"
                  className="w-full rounded-xl border border-white/10 shadow-lg"
                />
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-4 font-medium uppercase tracking-wide">Jälkeen — Selainpeli</p>
              <img
                src="/screenshots/web-map.png"
                alt="Selainpeli — interaktiivinen maailmankartta lentokenttämarkkereilla"
                className="w-full rounded-xl border border-white/10 shadow-lg"
              />
            </div>
          </div>
        </section>

        {/* Section 3 — Järjestelmäarkkitehtuuri */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Järjestelmäarkkitehtuuri</h2>
          <p className="text-sm text-gray-400 mb-5">Klikkaa komponenttia nähdäksesi lisätietoja.</p>
          <div className="flex flex-nowrap items-center justify-center gap-3 overflow-x-auto">
            {ARCH_NODES.map((node, i) => (
              <div key={node.id} className="flex items-center gap-3">
                <button
                  onClick={() => setActiveNode(activeNode === node.id ? null : node.id)}
                  className={`rounded-xl border px-6 py-5 flex flex-col items-center gap-3 min-w-[140px] transition-all ${
                    activeNode === node.id
                      ? 'bg-blue-600 border-blue-400 shadow-lg shadow-blue-900/40'
                      : 'bg-gray-800 border-white/20 hover:border-white/50 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {node.logos.map((logo) => (
                      <img
                        key={logo.alt}
                        src={logo.src}
                        alt={logo.alt}
                        className={`${logo.alt === 'MySQL' ? 'h-14' : 'h-10'} w-auto object-contain`}
                      />
                    ))}
                  </div>
                </button>
                {i < ARCH_NODES.length - 1 && (
                  <span className="text-white/30 text-xl font-light">→</span>
                )}
              </div>
            ))}
          </div>
          {activeNode && (() => {
            const node = ARCH_NODES.find((n) => n.id === activeNode)!;
            return (
              <div className="mt-5 rounded-xl bg-gray-800 border border-blue-400/30 p-5 space-y-3">
                <div>
                  <span className="font-bold text-blue-300 text-base">{node.label}</span>
                  <span className="text-gray-400 text-sm ml-2">— {node.desc}</span>
                </div>
                <ul className="space-y-2">
                  {node.details.map((detail) => (
                    <li key={detail} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-blue-400 mt-0.5 shrink-0">•</span>
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })()}
        </section>

        {/* Section 4 — Teknologiat */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Teknologiat</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {TECH_STACK.map((tech) => (
              <div key={tech.name} className="rounded-lg border border-white/10 bg-gray-900 p-4 space-y-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={tech.logo} alt={tech.name} className="h-7 w-auto object-contain" />
                <p className="font-bold text-sm">{tech.name}</p>
                <p className="text-xs text-gray-400">{tech.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Section 5 — Tietokantaratkaisu */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Tietokantaratkaisu</h2>

          <p className="text-sm text-gray-400 mb-5">Klikkaa taulukkoa nähdäksesi sarakkeet ja toteutushuomiot.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {DB_TABLES.map((table) => (
              <button
                key={table.name}
                onClick={() => setActiveTable(activeTable === table.name ? null : table.name)}
                className={`rounded-xl border p-5 text-left transition-all w-full ${
                  activeTable === table.name
                    ? 'border-blue-400 bg-gray-800 shadow-lg shadow-blue-900/20'
                    : 'border-white/20 bg-gray-900 hover:border-white/40'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold font-mono text-base">{table.name}</span>
                  <span className="text-xs text-gray-400">
                    {activeTable === table.name ? '▲ sulje' : `${table.columns.length} sarakketta ▼`}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mb-2">{table.role}</p>
                {activeTable === table.name && (
                  <div className="mt-3 space-y-3">
                    <ul className="space-y-1 border-t border-white/10 pt-3">
                      {table.columns.map((col) => (
                        <li
                          key={col}
                          className={`font-mono text-xs ${col.includes('→') ? 'text-yellow-400' : 'text-gray-300'}`}
                        >
                          {col}
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-blue-300 border-t border-white/10 pt-3 leading-relaxed">
                      💡 {table.notes}
                    </p>
                  </div>
                )}
              </button>
            ))}
          </div>

          <p className="text-xs text-gray-500 font-mono mb-8">
            Vierasavaimet: game.current_airport → airport.ident · game.user_id → users.id · goal.airport_ident → airport.ident
          </p>

          <h3 className="text-lg font-semibold mb-4 text-gray-200">Toteutuksen erikoisuudet</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {DB_INSIGHTS.map((insight) => (
              <div key={insight.title} className="rounded-lg border border-white/10 bg-gray-900 p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{insight.icon}</span>
                  <span className="font-semibold text-sm">{insight.title}</span>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">{insight.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Section 6 — Mitä opittiin */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Mitä opittiin?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-lg border border-white/10 bg-gray-900 p-5">
              <h3 className="font-bold mb-3">💡 Mitä opittiin</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>Full-stack TypeScript + Python</li>
                <li>Phaser.js canvas-ohjelmointi</li>
                <li>JWT-autentikointi</li>
                <li>React-Leaflet karttaintegraatio</li>
                <li>Pilvideploy (Vercel + Render + Aiven)</li>
              </ul>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-5">
              <h3 className="font-bold mb-3">😤 Mikä oli vaikeaa</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>Phaser.js + Next.js SSR-konfliktit</li>
                <li>MariaDB vs MySQL -yhteensopivuus</li>
                <li>Render free tier cold start</li>
                <li>Leaflet-ikonien resoluutio Next.js:ssä</li>
              </ul>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-5">
              <h3 className="font-bold mb-3">🔄 Mitä tekisin toisin</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>Suunnittelisin tietokantakaavion ensin</li>
                <li>Lisäisin syötetarkistuksen heti alussa</li>
                <li>Kirjoittaisin integraatiotestit aikaisemmin</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section 7 — Seuraavaksi */}
        <section>
          <h2 className="text-2xl font-bold mb-8 border-b border-white/10 pb-3">Seuraavaksi — v0.2</h2>
          <div className="rounded-lg border border-blue-500/30 bg-blue-950/30 p-8 text-center space-y-3">
            <span className="text-4xl">🌐</span>
            <h3 className="text-xl font-bold">Moninpeli WebSocket-yhteydellä</h3>
            <p className="text-gray-300 max-w-lg mx-auto">
              Useampi pelaaja voi pelata samassa lentokentässä samanaikaisesti. Reaaliaikaiset tulokset ja pisteet päivittyvät kaikille pelaajille heti.
            </p>
          </div>
        </section>

      </main>
    </div>
  );
}
