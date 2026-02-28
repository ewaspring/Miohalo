export const metadata = {
  title: 'Miohalo · Agentic Symbolic Orchestration',
  description: 'A homepage describing Miohalo and the cuneiform-to-26 symbolic bridge vision.',
};

import './globals.css';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
