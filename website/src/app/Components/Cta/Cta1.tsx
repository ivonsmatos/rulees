import Image from "next/image";

const Cta1 = () => {
    return (
<section className="cs_cta cs_style_1">
      <div className="cs_cta_content_wrapper cs_accent_bg cs_radius_30 cs_bg_filed" data-src="assets/img/cta-bg-1.svg">
        <div className="cs_height_60 cs_height_lg_60"></div>
        <div className="container">
          <div className="row cs_gap_y_40 align-items-center">
            <div className="col-lg-6 order-lg-2">
              <div className="cs_cta_thumbnail">
                <Image src="/assets/img/cta-img-1.png" alt="img" width={536} height={377}   />   
              </div>
            </div>
            <div className="col-lg-6 order-lg-1">
              <div className="cs_cta_text">
                <h2 className="cs_fs_48 cs_semibold cs_white_color cs_mb_20 text-capitalize wow fadeInDown">Let’s download free from apple and play store</h2>
                <p className="cs_white_color cs_mb_33">Highlight the most important features and functionalities of the app. Use concise descriptions or bullet points to emphasize what sets your app</p>
                <div className="cs_cta_btns">
                  <a href="#" aria-label="Download App button" className="cs_cta_btn cs_white_color">
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
                  <a href="#" aria-label="Download App button" className="cs_cta_btn cs_white_color">
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
        <div className="cs_height_60 cs_height_lg_60"></div>
      </div>
    </section>
    );
};

export default Cta1;