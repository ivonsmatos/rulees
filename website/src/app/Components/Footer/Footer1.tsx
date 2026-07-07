import Image from "next/image";
import Link from "next/link";

const Footer1 = () => {
    const bgImage = '/assets/img/footer-bg-2.svg'; 
    return (
 <footer className="cs_footer cs_style_1 cs_type_1 cs_accent_bg cs_bg_filed cs_white_color" style={{ backgroundImage: `url(${bgImage})`}}  >
      <div className="cs_height_130 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_footer_top position-relative">
          <ul className="cs_location_list cs_mp_0">
            <li>
              <span className="cs_location_icon cs_center cs_theme_color_4 cs_radius_100">
              <i className="bi bi-telephone-fill"></i></span>
              <a href="tel:01233337689" aria-label="Make a call link">0123-333-7689</a>
            </li>
            <li>
              <span className="cs_location_icon cs_center cs_theme_color_4 cs_radius_100">
             <i className="bi bi-envelope-fill"></i></span>
              <a href="mailto:info@example.com" aria-label="Send mail link">info@example.com</a>
            </li>
            <li>
              <span className="cs_location_icon cs_center cs_theme_color_4 cs_radius_100">
              <i className="bi bi-geo-alt-fill"></i></span>
              <p className="mb-0">5919 Trussville Crossings Pkwy, United States.</p>
            </li>
          </ul>
        </div>
        <div className="cs_footer_main">
          <div className="cs_footer_widget_wrapper">
            <div className="cs_footer_widget cs_text_widget">
              <div className="cs_brand cs_mb_32">
                <Image src="/assets/img/logo-2.svg" alt="img" width={194} height={36}   />
              </div>
              <p className="cs_mb_32">It involves the use of CRM software and strategies to effectively manage customer relationships, improve customer satisfaction, and drive business growth.</p>
              <div className="cs_social_links cs_style_1 cs_heading_color">
                <a href="#" aria-label="Social link"><i className="bi bi-facebook"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-linkedin"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-instagram"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-twitter-x"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-youtube"></i></a>
              </div>
            </div>
            <div className="cs_footer_widget cs_links_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_white_color cs_mb_29">Our Product</h3>
              <ul className="cs_footer_menu cs_mp_0">
                <li><Link href="/project/project-details" aria-label="Project details page link">Product Overview</Link></li>
                <li><Link href="/pricing" aria-label="Pricing page link">Pricing</Link></li>
                <li><Link href="/service" aria-label="Services page link">Services</Link></li>
                <li><Link href="/integrations" aria-label="Integrations page link">Integrations</Link></li>
                <li><Link href="#" aria-label="Security page link">Security</Link></li>
              </ul>
            </div>
            <div className="cs_footer_widget cs_help_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_white_color cs_mb_29">Our Company</h3>
              <ul className="cs_footer_menu cs_mp_0">
                <li><Link href="/about" aria-label="About page link">About Us</Link></li>
                <li><Link href="/team" aria-label="Team page link">Leadership Team</Link></li>
                <li><Link href="/contact" aria-label="Contact page link">Careers</Link></li>
                <li><Link href="/blog" aria-label="Blog page link">Press</Link></li>
              </ul>
            </div>
            <div className="cs_footer_widget cs_contact_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_white_color cs_mb_29">Resources</h3>
              <ul className="cs_footer_menu cs_mp_0">
                <li><a href="#" aria-label="Blog page link">Blog</a></li>
                <li><a href="#" aria-label="Events page link">Events</a></li>
                <li><a href="#" aria-label="Support page link">Support Center</a></li>
                <li><a href="#" aria-label="Demo page link">Get Demo</a></li>
                <li><a href="#" aria-label="Forum page link">Community Forums</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div className="cs_footer_bottom position-relative">
        <div className="container">
          <div className="cs_footer_text cs_white_color text-center">Copyright &copy; <span className="cs_getting_year"></span> Saaso theme by Themeservices</div>
        </div>
      </div>
    </footer>
    );
};

export default Footer1;