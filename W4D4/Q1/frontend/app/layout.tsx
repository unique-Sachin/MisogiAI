import './globals.css'

export const metadata = {
  title: 'HR Knowledge Assistant',
  description: 'AI-powered HR onboarding assistant',
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