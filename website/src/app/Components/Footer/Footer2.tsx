import Image from "next/image";
import Link from "next/link";

const Footer2 = () => {
    return (
 <footer className="cs_footer cs_style_1 cs_type_2 cs_accent_bg cs_bg_filed" data-src="assets/img/footer-bg-3.svg">
      <div className="cs_height_130 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_footer_top position-relative">
          <ul className="cs_location_list cs_mp_0">
            <li>
              <span className="cs_location_icon cs_center cs_heading_color cs_radius_100">
              <i className="bi bi-whatsapp"></i></span>
              <div className="cs_location_info cs_fs_18">
                <p className="cs_fs_14 cs_theme_color_4 mb-0">WHATSAPP</p>
                <a href="https://wa.me/5511941906079" target="_blank" rel="noopener" aria-label="Falar no WhatsApp" className="cs_white_color">(11) 94190-6079</a>
              </div>
            </li>
            <li>
              <span className="cs_location_icon cs_center cs_heading_color cs_radius_100">
              <i className="bi bi-envelope-fill"></i></span>
              <div className="cs_location_info cs_fs_18">
                <p className="cs_fs_14 cs_theme_color_4 mb-0">E-MAIL</p>
                <a href="mailto:contato@rulees.com.br" aria-label="Enviar e-mail">contato@rulees.com.br</a> <br/>
                <a href="mailto:suporte@rulees.com.br" aria-label="Enviar e-mail">suporte@rulees.com.br</a>
              </div>
            </li>
            <li>
              <span className="cs_location_icon cs_center cs_heading_color cs_radius_100">
              <i className="bi bi-telephone-fill"></i></span>
              <div className="cs_location_info cs_fs_18">
                <p className="cs_fs_14 cs_theme_color_4 mb-0">SITE</p>
                <a href="https://rulees.com.br" aria-label="Site do Rulees">rulees.com.br</a><br/>
                <a href="/contact" aria-label="Falar com o time">Fale com o time</a>
              </div>
            </li>
          </ul>
        </div>
        <div className="cs_footer_main cs_radius_30">
          <div className="cs_footer_desc">
            <div className="cs_brand">
               <Image src="/assets/img/rulees-logo-white.svg" alt="Rulees" width={160} height={53}   />
               <p className="cs_white_color cs_heading_font cs_fs_20 cs_mt_10 mb-0">Onde o negócio se define.</p>
            </div>
            <div className="cs_footer_desc_text">O Rulees transforma reuniões de negócio em regras claras, decisões e documentação rastreável. A IA descobre os requisitos, pessoas aprovam, e cada regra fica ligada à fala original — para times de produto e software houses que não podem errar requisito.</div>
          </div>
          <div className="cs_footer_header cs_radius_30">
            <ul className="cs_footer_menu cs_semibold cs_white_color cs_mp_0">
              <li><Link href="/" aria-label="Início">Início</Link></li>
              <li><Link href="/about" aria-label="Como funciona">Como funciona</Link></li>
              <li><Link href="/service" aria-label="Recursos">Recursos</Link></li>
              <li><Link href="/pricing" aria-label="Planos">Planos</Link></li>
              <li><Link href="/blog" aria-label="Blog">Blog</Link></li>
              <li><Link href="/contact" aria-label="Contato">Contato</Link></li>
            </ul>
            <div className="cs_social_links cs_style_1 cs_heading_color">
                <a href="#" aria-label="Social link"><i className="bi bi-facebook"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-linkedin"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-instagram"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-twitter-x"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-youtube"></i></a>
            </div>
          </div>
        </div>
        <div className="cs_footer_bottom position-relative">
          <div className="cs_footer_text cs_white_color text-center">&copy; <span className="cs_getting_year"></span> Rulees · rulees.com.br · Desenvolvido por <a href="https://scaledata.com.br" target="_blank" rel="noopener" aria-label="Scaledata">Scaledata</a></div>
        </div>
      </div>
    </footer>
    );
};

export default Footer2;