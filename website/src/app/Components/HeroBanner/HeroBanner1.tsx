import Image from "next/image";
import Link from "next/link";

const HeroBanner1 = () => {
      const bgImage = '/assets/img/hero-bg-2.jpg';
    return (
        <div>
            <section className="cs_hero cs_style_2 cs_bg_filed position-relative" style={{ backgroundImage: `url(${bgImage})`}}>
            <div className="container">
                <div className="cs_hero_text text-center position-relative">
                <p className="cs_hero_subtitle cs_heading_color cs_heading_font cs_mb_18 text-center">
                    <span className="cs_theme_color_4">
                        <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />                          
                    </span>
                    <span>Welcome To Saaso</span>
                    <span className="cs_theme_color_4">
                        <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                    </span>
                </p>
                <h1 className="cs_hero_title cs_fs_64 cs_mb_20 wow fadeInDown">Our SaaS Solution to Simplify <br/> Your Operations</h1>
                <p className="cs_hero_desc cs_mb_26">All the generators on the Internet tend to repeat predefined chunks as necessary, making <br/> this the first true generator on the Internet.All the generators on the Internet</p>
                <div className="cs_btns_group">
                    <Link href="/contact" aria-label="Get started button" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
                    <span>Get Started</span>
                    <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                    </Link>
                    <Link href="/about" aria-label="About page link" className="cs_btn cs_style_1 cs_outline cs_ cs_fs_14 cs_bold cs_heading_color text-uppercase">
                    <span>Learn More</span>
                    <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                    </Link>
                </div>
                <div className="cs_hero_shape_1 position-absolute">
                    <Image src="/assets/img/hero-shape-1.svg" alt="img" width={120} height={90}   />
                </div>
                </div>
                <div className="cs_hero_shape_2 position-absolute">
                    <Image src="/assets/img/hero-shape-2.svg" alt="img" width={73} height={77}   />
                </div>
            </div>
            </section>   

            <div className="cs_banner cs_style_1 position-relative">
                <div className="container">
                    <div className="cs_banner_thumbnail_wrapper">
                    <div className="cs_banner_thumbnail">
                        <Image src="/assets/img/banner-img-1.png" alt="img" width={1296} height={770}   />
                    </div>
                    <div className="cs_banner_thumbnail">
                        <Image src="/assets/img/phone-img-1.png" alt="img" width={428} height={702}   />
                    </div>
                    </div>
                </div>
            </div>           

        </div>
    );
};

export default HeroBanner1;