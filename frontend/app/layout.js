import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'FrontRow — Real-Time Seat-Level Event Ticketing Platform',
  description: 'High-concurrency event ticketing platform featuring real-time seat locks and AI seat recommendations.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
