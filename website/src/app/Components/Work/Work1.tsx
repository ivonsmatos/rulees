import Image from "next/image";

const Work1 = () => {
    return (
    <section className="cs_gray_bg_2 position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="row cs_gap_y_40 position-relative z-1">
          <div className="col-lg-6 order-lg-2">
            <div className="cs_workink_process_heading cs_center_column position-relative">
              <div className="cs_section_heading cs_style_1 cs_mb_11 z-1">
                <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                  <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  <span>How It work</span>
                  <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                </div>
                <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInUp">Lets Utilize Optimum In Three Easy Actions.</h2>
                <p className="cs_card_desc cs_mb_22">All the generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet.</p>
              </div>
              <div className="cs_process_thumbnail z-1">
                <Image src="/assets/img/human-1.png" alt="img" width={438} height={408}   />
              </div>
              <div className="cs_vector_shape position-absolute bottom-0 start-0">
                <Image src="/assets/img/vector-7.svg" alt="img" width={597} height={473}   />
              </div>
            </div>
          </div>
          <div className="col-lg-6 order-lg-1">
            <div className="cs_iconbox_wrapper_2">
              <div className="cs_iconbox cs_style_2">
                <span className="cs_iconbox_icon cs_center cs_accent_bg cs_mb_18">
                  <Image src="/assets/img/icons/home.svg" alt="img" width={33} height={30}   />
                </span>
                <h3 className="cs_fs_24 cs_semibold cs_mb_4">Create your account</h3>
                <p className="mb-0">All the generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet.</p>
              </div>
              <div className="cs_iconbox cs_style_2">
                <span className="cs_iconbox_icon cs_bg_1 cs_center cs_mb_18">
                  <Image src="/assets/img/icons/products.svg" alt="img" width={30} height={30}   />
                </span>
                <h3 className="cs_fs_24 cs_semibold cs_mb_4">Connect your product</h3>
                <p className="mb-0">All the generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet.</p>
              </div>
              <div className="cs_iconbox cs_style_2">
                <span className="cs_iconbox_icon cs_bg_2 cs_center cs_mb_18">
                  <Image src="/assets/img/icons/analytics.svg" alt="img" width={30} height={30}   />
                </span>
                <h3 className="cs_fs_24 cs_semibold cs_mb_4">Track Analytics your account</h3>
                <p className="mb-0">All the generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="cs_star_shape_4 position-absolute">
        <Image src="/assets/img/star-shape.svg" alt="img" width={67} height={67}   />
      </div>
      <div className="cs_height_0 cs_height_lg_80"></div>
    </section>
    );
};

export default Work1;