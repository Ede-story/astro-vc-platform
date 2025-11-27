import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'StarMeet - Астрологический калькулятор',
  description: 'Рассчитайте свою ведическую натальную карту на StarMeet',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className="text-white antialiased">
        {children}
      </body>
    </html>
  )
}
