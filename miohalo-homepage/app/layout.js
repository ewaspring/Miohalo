export const metadata = {
  title: 'Miohalo · Agentic Symbolic Orchestration',
  description: 'A homepage describing Miohalo and the cuneiform-to-26 symbolic bridge vision.',
};

import './globals.css';
import SiteNav from './components/SiteNav';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <SiteNav />
        {children}
      </body>
    </html>
  );
}
