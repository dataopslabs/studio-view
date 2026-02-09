import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Observe2Agent - AI QA Automation Platform',
  description: 'Transform business process videos into executable automation workflows',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
