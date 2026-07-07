import { Sora, DM_Sans } from "next/font/google";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import "slick-carousel/slick/slick.css";
import "./assets/main.css";

const sora = Sora({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--body-color-font',
});

const dm_sans = DM_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--body-color-font',
});

const siteUrl = 'https://rulees.com.br';

export const metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    absolute: 'Rulees — Inteligência de Requisitos com IA | Reuniões viram regras rastreáveis',
    default: 'Rulees — Inteligência de Requisitos com IA',
    template: '%s | Rulees',
  },
  description:
    'O Rulees transforma reuniões de negócio em regras claras, decisões e documentação rastreável. A IA descobre os requisitos, pessoas aprovam, e cada regra fica ligada à fala original. Feito para software houses e times de produto.',
  keywords: [
    'inteligência de requisitos',
    'regras de negócio',
    'IA para reuniões',
    'transcrição de reunião',
    'Rules Ledger',
    'documentação de requisitos',
    'histórias de usuário',
    'critérios de aceite',
    'rastreabilidade',
    'exportar para Jira',
    'exportar para Confluence',
    'software house',
    'requirements intelligence',
  ],
  authors: [{ name: 'Rulees' }],
  creator: 'Rulees',
  publisher: 'Rulees',
  alternates: { canonical: '/' },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large', 'max-snippet': -1 },
  },
  icons: {
    icon: [{ url: '/assets/img/rulees-icon.svg', type: 'image/svg+xml' }, { url: '/favicon.ico' }],
    apple: '/assets/img/rulees-icon.svg',
  },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: siteUrl,
    siteName: 'Rulees',
    title: 'Rulees — Inteligência de Requisitos com IA',
    description:
      'Reuniões viram regras de negócio rastreáveis. A IA descobre os requisitos, pessoas aprovam, e cada decisão fica ligada à fala original.',
    images: [{ url: '/assets/img/rulees/hero-meeting.jpg', width: 1200, height: 630, alt: 'Equipe em reunião usando o Rulees' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Rulees — Inteligência de Requisitos com IA',
    description: 'Reuniões viram regras de negócio rastreáveis, com IA e aprovação humana.',
    images: ['/assets/img/rulees/hero-meeting.jpg'],
  },
};

const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      '@id': `${siteUrl}/#organization`,
      name: 'Rulees',
      url: siteUrl,
      logo: `${siteUrl}/assets/img/rulees-logo.svg`,
      description:
        'Plataforma de inteligência de requisitos com IA que transforma reuniões em regras de negócio rastreáveis.',
      email: 'contato@rulees.com.br',
      sameAs: [
        'https://www.linkedin.com/company/rulees',
        'https://github.com/rulees',
      ],
    },
    {
      '@type': 'WebSite',
      '@id': `${siteUrl}/#website`,
      url: siteUrl,
      name: 'Rulees',
      publisher: { '@id': `${siteUrl}/#organization` },
      inLanguage: 'pt-BR',
    },
    {
      '@type': 'SoftwareApplication',
      name: 'Rulees',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web',
      description:
        'AI Requirements Intelligence Platform: captura reuniões, extrai regras de negócio com IA, mantém um Rules Ledger com aprovação humana e gera documentação rastreável com exportação para Jira e Confluence.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'BRL' },
      url: siteUrl,
    },
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <head>
        <meta name="author" content="Rulees" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      </head>
      <body className={`${sora.variable} ${dm_sans.variable}`}>
        {children}
      </body>
    </html>
  );
}
