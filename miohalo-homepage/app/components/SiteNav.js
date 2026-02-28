'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

const timeline = [
  {
    title: 'Phase 1 · Seed 5',
    text: 'A / E / I / U / X 初始命中',
  },
  {
    title: 'Phase 2 · Full 26',
    text: 'A–Z 全量映射完成并持续修订',
  },
];

export default function SiteNav() {
  const pathname = usePathname();
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const saved = window.localStorage.getItem('miohalo-theme');
    const nextTheme = saved === 'light' ? 'light' : 'dark';
    setTheme(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    window.localStorage.setItem('miohalo-theme', theme);
  }, [theme]);

  const isLight = theme === 'light';

  return (
    <header className="siteHeader">
      <div className="siteHeaderInner">
        <div className="navRow">
          <nav className="navLinks" aria-label="Primary">
            <Link className={pathname === '/' ? 'active' : ''} href="/">Home</Link>
            <Link className={pathname === '/cuneiform-map' ? 'active' : ''} href="/cuneiform-map">Cuneiform Map</Link>
            {pathname !== '/' && (
              <Link href="/" aria-label="Back to homepage">← Back Home</Link>
            )}
          </nav>

          <button
            className="themeToggle"
            type="button"
            onClick={() => setTheme(isLight ? 'dark' : 'light')}
            aria-label="Toggle light mode"
          >
            {isLight ? '🌙 Dark mode' : '☀️ Light mode'}
          </button>
        </div>

        <div className="timeline" aria-label="cuneiform mapping timeline">
          {timeline.map((item, index) => (
            <article className="timelineItem" key={item.title}>
              <span className="timelineDot">{index + 1}</span>
              <div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </header>
  );
}
