import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'StarMeet - Join',
  description: 'Create your astrological profile on StarMeet',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
