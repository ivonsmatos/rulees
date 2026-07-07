import Image from 'next/image';
import React from 'react';

const Choose3 = () => {
    return (
 <section className="position-relative overflow-hidden">
      <div className="container">
        <div className="cs_card cs_style_1 cs_type_2">
          <div className="row cs_gap_y_50 position-relative z-1">
            <div className="col-lg-6">
              <div className="cs_card_thumbnail position-relative">
                <Image src="/assets/img/about-img-3.png" alt="img" width={636} height={702}   /> 
                <div className="cs_vector_shape_3 position-absolute">
                  <Image src="/assets/img/vector-2.svg" alt="img" width={636} height={504}   /> 
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_28">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                   <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                    <span>Why Choose App</span>
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow fadeInDown">Why Saaso Is The Right Choice For You</h2>
                </div>
                <p className="cs_card_desc cs_mb_22">All the generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet.</p>
                <div className="cs_iconbox_wrapper_1">
                  <div className="cs_iconbox cs_style_1">
                    <span className="cs_iconbox_icon cs_center cs_accent_bg cs_white_color cs_radius_15">
                      <Image src="/assets/img/icons/adons.svg" alt="img" width={46} height={46}   /> 
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Extensions & Addons</h3>
                      <p className="mb-0">Our SEO strategies will attract more qualified visitors to your website, bringing you closer.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_1">
                    <span className="cs_iconbox_icon cs_center cs_bg_1 cs_white_color cs_radius_15">
                      <Image src="/assets/img/icons/interface.svg" alt="img" width={46} height={46}   /> 
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Friendly Interface</h3>
                      <p className="mb-0">Increased website traffic and the improved rankings naturally lead to greater brand awareness.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_1">
                    <span className="cs_iconbox_icon cs_center cs_bg_2 cs_white_color cs_radius_15">
                      <Image src="/assets/img/icons/fast-easy.svg" alt="img" width={42} height={46}   /> 
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Fast & Easy</h3>
                      <p className="mb-0">By attracting qualified the traffic and optimizing your website for conversions, we will help you.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_vector_shape_4 position-absolute">
          <Image src="/assets/img/vector-3.svg" alt="img" width={235} height={529}   /> 
        </div>
      </div>
      <div className="cs_height_46 cs_height_lg_40"></div>
    </section>
    );
};

export default Choose3;