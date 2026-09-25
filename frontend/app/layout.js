export const metadata = {
  title: 'FrontRow — Seat-Level Event Ticketing Platform',
  description: 'High-concurrency real-time seat reservation and ticketing platform.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'sans-serif' }}>
        {children}
      </body>
    </html>
  );
}
