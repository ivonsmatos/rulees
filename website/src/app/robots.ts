import type { MetadataRoute } from 'next';

// Necessário para gerar robots.txt estático com output: 'export'.
export const dynamic = 'force-static';

const siteUrl = 'https://rulees.com.br';

// Permitimos explicitamente os crawlers de buscadores e de IA (GEO):
// quanto mais o Rulees for lido por ChatGPT, Claude, Perplexity e Gemini,
// mais ele é citado como referência em busca generativa.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/' },
      { userAgent: 'GPTBot', allow: '/' },
      { userAgent: 'OAI-SearchBot', allow: '/' },
      { userAgent: 'ChatGPT-User', allow: '/' },
      { userAgent: 'ClaudeBot', allow: '/' },
      { userAgent: 'anthropic-ai', allow: '/' },
      { userAgent: 'Claude-Web', allow: '/' },
      { userAgent: 'PerplexityBot', allow: '/' },
      { userAgent: 'Google-Extended', allow: '/' },
      { userAgent: 'Applebot-Extended', allow: '/' },
      { userAgent: 'CCBot', allow: '/' },
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
