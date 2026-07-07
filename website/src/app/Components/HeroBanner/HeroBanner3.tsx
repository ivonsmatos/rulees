import Image from "next/image";

const HeroBanner3 = () => {
      const bgImage = '/assets/img/hero-bg-1.svg';
    return (
    <section className="cs_hero cs_style_1">
      <div className="cs_hero_content cs_accent_bg cs_bg_filed cs_radius_50 position-relative" style={{ backgroundImage: `url(${bgImage})`}}>
        <div className="container">
          <div className="row cs_gap_y_40 align-items-center">
            <div className="col-lg-5 order-lg-2">
              <div className="cs_hero_thumbnail">
                <Image src="/assets/img/hero-img-1.png" alt="img" width={749} height={641}   />
              </div>
            </div>
            <div className="col-lg-7 order-lg-1">
              <div className="cs_hero_text cs_section_heading cs_style_1 position-relative z-2">
                <p className="cs_hero_subtitle cs_white_color cs_heading_font cs_mb_22 text-center">
                  <span className="cs_theme_color_4">
                    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M7.5 0L9.52568 5.47432L15 7.5L9.52568 9.52568L7.5 15L5.47432 9.52568L0 7.5L5.47432 5.47432L7.5 0Z" fill="currentColor"/>
                    </svg>
                  </span>
                  <span>Best Solution in 1 Place</span>
                  <span className="cs_theme_color_4">
                    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M7.5 0L9.52568 5.47432L15 7.5L9.52568 9.52568L7.5 15L5.47432 9.52568L0 7.5L5.47432 5.47432L7.5 0Z" fill="currentColor"/>
                    </svg>
                  </span>
                </p>
                <h1 className="cs_hero_title cs_fs_64 cs_white_color cs_mb_15 wow fadeInUp">Easy Productivity for Modern Businesses</h1>
                <p className="cs_hero_desc cs_white_color cs_mb_28">All the generators on the Internet tend to repeat predefined chunks as necessary, <br/> making this the first true generator on the Internet.</p>
                <div className="cs_btns_group">
                  <a href="#" aria-label="Get started button" className="cs_btn cs_style_1 cs_theme_bg_4 cs_fs_14 cs_bold cs_heading_color text-uppercase">
                  <span>Down load now</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                  </a>
                  <div className="cs_client_info_wrapper">
                     <Image src="/assets/img/customers-group.png" alt="img" width={147} height={57}   />
                    <div>
                      <h3 className="cs_fs_30 cs_semibold cs_white_color">3.5k+</h3>
                      <p className="cs_white_color mb-0">Active Customer</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    );
};

export default HeroBanner3;