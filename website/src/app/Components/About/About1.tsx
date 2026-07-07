import Image from "next/image";

const About1 = () => {
    return (
<section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_card cs_style_1">
          <div className="row cs_gap_y_50 position-relative z-1">
            <div className="col-lg-5">
              <div className="cs_card_thumbnail position-relative">
                <Image src="/assets/img/about-img-1.png" alt="img" width={486} height={548}   />  
                <div className="cs_about_mask_shape_1 position-absolute">
                  <Image src="/assets/img/about-shape-1.png" alt="img" width={526} height={363}   />  
                </div>
                <div className="cs_elipse_1 cs_radius_100 position-absolute"></div>
              </div>
            </div>
            <div className="col-lg-7">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_28">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                   <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />  
                    <span> About Our App</span>
                   <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />  
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow fadeInUp">Designed for the upcoming small business generation</h2>
                </div>
                <p className="cs_card_desc cs_mb_22">Incorporate visually appealing elements such as high-quality images, videos, or graphics that resonate with the target audience and complement the overall design of the page. Ensure that the landing page is optimized for various devices.</p>
                <ul className="cs_list cs_style_1 cs_mp_0">
                  <li>
                    <Image src="/assets/img/icons/checkbox.svg" alt="img" width={30} height={30}   />  
                    <h3 className="cs_fs_18 cs_semibold mb-0">with our marketing and technological solutions.</h3>
                  </li>
                  <li>
                    <Image src="/assets/img/icons/checkbox.svg" alt="img" width={30} height={30}   />  
                    <h3 className="cs_fs_18 cs_semibold mb-0">All throughout the world, people trust us.</h3>
                  </li>
                  <li>
                    <Image src="/assets/img/icons/checkbox.svg" alt="img" width={30} height={30}   />  
                    <h3 className="cs_fs_18 cs_semibold mb-0">Start Your 14 Days Free Trials Today!</h3>
                  </li>
                </ul>
                <a href="#" aria-label="App download button" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_white_color cs_bold text-uppercase">
                <span>Download App</span>
                <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                </a>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_star_shape_1 position-absolute">
          <Image src="/assets/img/star-shape.svg" alt="img" width={67} height={67}   />  
        </div>
        <div className="cs_vector_shape_1 position-absolute">
          <Image src="/assets/img/dna-shape.png" alt="img" width={89} height={150}   />  
        </div>
      </div>
      <div className="cs_height_46 cs_height_lg_40"></div>
    </section>
    );
};

export default About1;