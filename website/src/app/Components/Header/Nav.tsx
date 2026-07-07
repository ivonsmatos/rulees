import Link from 'next/link';
import DropDown from './DropDown';

export default function Nav({ setMobileToggle }) {
  return (
    <ul className="cs_nav_list fw-medium">
      <li>
        <Link href="/" onClick={() => setMobileToggle(false)}>Início</Link>
      </li>

      <li>
        <Link href="/about" onClick={() => setMobileToggle(false)}>Como funciona</Link>
      </li>

      <li className="menu-item-has-children">
        <Link href="/service" onClick={() => setMobileToggle(false)}>Recursos</Link>
        <DropDown>
          <ul>
            <li>
              <Link href="/service" onClick={() => setMobileToggle(false)}>Visão geral</Link>
            </li>
            <li>
              <Link href="/service/service-details" onClick={() => setMobileToggle(false)}>Rules Ledger</Link>
            </li>
            <li>
              <Link href="/integrations" onClick={() => setMobileToggle(false)}>Integrações</Link>
            </li>
          </ul>
        </DropDown>
      </li>

      <li>
        <Link href="/pricing" onClick={() => setMobileToggle(false)}>Planos</Link>
      </li>

      <li className="menu-item-has-children">
        <Link href="#">Recursos do site</Link>
        <DropDown>
          <ul>
            <li>
              <Link href="/project" onClick={() => setMobileToggle(false)}>Casos de uso</Link>
            </li>
            <li>
              <Link href="/faq" onClick={() => setMobileToggle(false)}>Perguntas frequentes</Link>
            </li>
          </ul>
        </DropDown>
      </li>

      <li className="menu-item-has-children">
        <Link href="/blog" onClick={() => setMobileToggle(false)}>Blog</Link>
        <DropDown>
          <ul>
            <li>
              <Link href="/blog" onClick={() => setMobileToggle(false)}>Artigos</Link>
            </li>
            <li>
              <Link href="/blog/blog-details" onClick={() => setMobileToggle(false)}>Exemplo de artigo</Link>
            </li>
          </ul>
        </DropDown>
      </li>

      <li>
        <Link href="/contact" onClick={() => setMobileToggle(false)}>Contato</Link>
      </li>
    </ul>
  );
}
