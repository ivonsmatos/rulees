import Image from "next/image";
import Link from "next/link";

const Footer3 = () => {
    const bgImage = 'assets/img/footer-bg-1.svg';
    return (
    <footer className="cs_footer cs_style_1 cs_bg_filed cs_heading_color" style={{ backgroundImage: `url(${bgImage})`}} >
      <div className="cs_height_130 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_footer_top position-relative">
          <div className="cs_newsletter cs_style_1">
            <div className="cs_newsletter_text">
              <h2 className="cs_fs_48 cs_semibold cs_mb_20 wow fadeInDown">Subscribe our Newsletter</h2>
              <p className="cs_heading_color mb-0">Start with a free one-month trial. No purchase is necessary.</p>
            </div>
            <form className="cs_newsletter_form cs_fs_14">
              <div className="cs_input_wrapper position-relative">
                <span className="cs_input_icon">
                  <Image src="/assets/img/icons/mail.svg" alt="img" width={17} height={12}   />
                </span>
                <input type="email" name="email" placeholder="Your Email Address" />
              </div>
              <button type="submit" aria-label="Subscribe button" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">Subscribe Now</button>
            </form>
          </div>
        </div>
        <div className="cs_footer_main">
          <div className="cs_footer_widget_wrapper">
            <div className="cs_footer_widget cs_text_widget">
              <div className="cs_brand cs_mb_32">
                <Image src="/assets/img/logo.svg" alt="img" width={194} height={36}   />
              </div>
              <p className="cs_mb_32">It involves the use of CRM software and strategies to effectively manage customer relationships, improve customer satisfaction, and drive business growth. </p>
              <div className="cs_social_links cs_style_1 cs_heading_color">
                <a href="#" aria-label="Social link"><i className="bi bi-facebook"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-linkedin"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-instagram"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-twitter-x"></i></a>
                <a href="#" aria-label="Social link"><i className="bi bi-youtube"></i></a>
              </div>
            </div>
            <div className="cs_footer_widget cs_links_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_mb_29">Useful Links</h3>
              <ul className="cs_footer_menu cs_mp_0">
              <li><Link href="/" aria-label="Home page link">Home</Link></li>
              <li><Link href="/about" aria-label="About page link">About Us</Link></li>
              <li><Link href="/service" aria-label="Services page link">Services</Link></li>
              <li><Link href="/project" aria-label="Project page link">Projects</Link></li>
              <li><Link href="/blog" aria-label="Blog page link">Blog</Link></li>
              </ul>
            </div>
            <div className="cs_footer_widget cs_help_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_mb_29">Help & Support</h3>
              <ul className="cs_footer_menu cs_mp_0">
                <li><a href="#" aria-label="Faqs page link">FAQs</a></li>
                <li><a href="#" aria-label="Support page link">Support</a></li>
                <li><Link href="/integrations" aria-label="Integrations page link">How It Work</Link></li>
                <li><a href="#" aria-label="Terms & conditions page link">Terms & Conditions</a></li>
                <li><a href="#" aria-label="Privacy policy page link">Privacy Policy</a></li>
              </ul>
            </div>
            <div className="cs_footer_widget cs_contact_widget">
              <h3 className="cs_footer_widget_title cs_fs_24 cs_semibold cs_mb_29">Lets Try out</h3>
              <div className="cs_cta_btns">
                <a href="#" aria-label="Download App button" className="cs_cta_btn cs_heading_bg cs_white_color">
                  <span className="cs_btn_icon">
                    <svg width="26" height="32" viewBox="0 0 26 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21.7383 16.7637C21.7383 16.9004 21.5332 20.9336 25.9766 23.0527C25.1562 25.582 22.2852 31.1875 18.9355 31.1875C17.0215 31.1875 15.9277 29.957 13.7402 29.957C11.4844 29.957 10.2539 31.1875 8.54492 31.1875C5.26367 31.3242 2.11914 25.1719 1.23047 22.6426C0.546875 20.7285 0.273438 18.8828 0.273438 17.1055C0.273438 11.0215 4.30664 8.08203 8.13477 8.01367C9.98047 8.01367 12.3047 9.3125 13.3301 9.3125C14.2871 9.3125 16.9531 7.74023 19.4141 7.94531C21.9434 8.15039 23.8574 9.10742 25.1562 10.9531C22.9004 12.3887 21.7383 14.2344 21.7383 16.7637ZM17.9102 5.55273C16.543 7.125 14.9023 8.01367 13.125 7.87695C12.9883 6.03125 13.6719 4.32227 14.9023 2.95508C15.9961 1.72461 17.9102 0.699219 19.5508 0.5625C19.5508 1.31445 19.7559 3.36523 17.9102 5.55273Z" fill="currentColor"/>
                    </svg>
                  </span>
                  <div className="cs_btn_text">
                    <p className="cs_fs_15 mb-0">Get it on</p>
                    <p className="cs_fs_18 cs_medium mb-0">App Store</p>
                  </div>
                </a>
                <a href="#" aria-label="Download App button" className="cs_cta_btn cs_white_bg cs_heading_color">
                  <span className="cs_btn_icon">
                    <svg width="28" height="31" viewBox="0 0 28 31" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M18.043 14.5195L21.5586 11.0039L5.09375 1.51172L18.043 14.5195ZM1.75391 0.75C0.992188 1.16016 0.464844 1.92188 0.464844 2.85938V28.6992C0.464844 29.6367 0.992188 30.3984 1.75391 30.75L16.7539 15.75L1.75391 0.75ZM26.6562 13.9922L23.1992 12L19.332 15.75L23.1992 19.5586L26.7148 17.5664C27.7695 16.7461 27.7695 14.8125 26.6562 13.9922ZM5.09375 29.9883L21.5586 20.5547L18.043 17.0391L5.09375 29.9883Z" fill="currentColor"/>
                    </svg>
                  </span>
                  <div className="cs_btn_text">
                    <p className="cs_fs_15 mb-0">Get it on</p>
                    <p className="cs_fs_18 cs_medium mb-0">Google Play</p>
                  </div>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="cs_footer_bottom cs_accent_bg">
        <div className="container">
          <div className="cs_footer_text cs_white_color text-center">Copyright &copy; <span className="cs_getting_year"></span> Saaso theme by Themeservices</div>
        </div>
      </div>
    </footer>
    );
};

export default Footer3;