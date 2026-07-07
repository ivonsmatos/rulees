/** @type {import('next').NextConfig} */
const nextConfig = {
  // Exportação 100% estática (HTML/CSS/JS) — ideal para Cloudflare Workers/Pages (free).
  output: 'export',
  // next/image sem servidor de otimização (obrigatório no export estático).
  images: { unoptimized: true },
  // Gera /pagina/index.html — URLs limpas em hospedagem estática.
  trailingSlash: true,
};

export default nextConfig;
