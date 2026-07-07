"use client"
import Image from "next/image";
import Link from "next/link";
import { useRef } from "react";
import Slider from "react-slick";

const Blog1 = () => {

        const settings = {
        dots: false,
        infinite: true,
        speed: 2000,
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: false,
        swipeToSlide: true,
        autoplay: true,
        autoplaySpeed: 4000,        
        responsive: [
          {
            breakpoint: 1399,
            settings: {
              slidesToShow: 3,
            }
          },
          {
            breakpoint: 1199,
            settings: {
              slidesToShow: 3,
            }
          },{
            breakpoint: 575,
            settings: {
              slidesToShow: 1,
            }
          }
        ]
      };  

      const sliderRef = useRef(null);

      const next = () => {
        sliderRef.current.slickNext();
      };
    
      const previous = () => {
        sliderRef.current.slickPrev();
      }; 

    const blogContent = [
        {img:'/assets/img/post-img-4.jpg', title:'How to Comprehensive at SaaS Developments', category:'Development'},
        {img:'/assets/img/post-img-5.jpg', title:'6 Essential Tips for Big Commerce Stores', category:'Technology'},
        {img:'/assets/img/post-img-6.jpg', title:'Empowering Startups & Small Businesses', category:'Marketing'},
        {img:'/assets/img/post-img-1.jpg', title:'How to Comprehensive at SaaS Developments', category:'Development'},
      ];


    return (
 <section className="cs_slider cs_style_1 cs_slider_gap_30 position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_type_1 cs_mb_60">
          <div className="cs_section_heading_left">
            <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
              <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
              <span>Blog & Articles</span>
              <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
            </div>
            <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow fadeInDown">News & Blog Insight Insights</h2>
          </div>
          <div className="cs_section_heading_right">
            <div className="cs_slider_arrows cs_style_1 cs_type_1">
              <div onClick={previous} className="cs_left_arrow rounded-circle cs_center cs_white_bg cs_heading_color slick-arrow">
                <i className="bi bi-arrow-left"></i>
              </div>
              <div onClick={next} className="cs_right_arrow rounded-circle cs_center cs_white_bg cs_heading_color slick-arrow">
                <i className="bi bi-arrow-right"></i>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_slider_container" data-autoplay="0" data-loop="1" data-speed="600" data-center="0" data-variable-width="0" data-slides-per-view="responsive" data-xs-slides="1" data-sm-slides="2" data-md-slides="2" data-lg-slides="3" data-add-slides="3">
          <div className="cs_slider_wrapper cs_slider_gap_301">
            <Slider ref={sliderRef} {...settings}>
            {blogContent.map((item, i) => (
            <div key={i} className="cs_slide">
              <article className="cs_post cs_style_1 cs_type_1 cs_radius_20">
                <Link href="/blog/blog-details" aria-label="Reading details post link" className="cs_post_thumbnail cs_mb_15 position-relative overflow-hidden">
                <Image src={item.img} alt="img" width={378} height={264}   /> 
                <span className="cs_post_category cs_fs_14 cs_medium cs_heading_bg cs_white_color position-absolute">{item.category}</span>
                </Link>
                <div className="cs_post_content">
                  <div className="cs_post_meta_wrapper cs_mb_12">
                    <div className="cs_post_meta">
                      <span><i className="bi bi-person"></i></span>
                      <span>Adam Smith</span>
                    </div>
                    <div className="cs_post_meta">
                      <span><i className="bi bi-calendar-check-fill"></i></span>
                      <span>11 Jan, 2025</span>
                    </div>
                  </div>
                  <h3 className="cs_post_title cs_fs_24 cs_semibold cs_mb_13"><Link href="/blog/blog-details" aria-label="Reading details post link">{item.title}</Link></h3>
                  <Link href="/blog/blog-details" aria-label="Reading details post link" className="cs_post_btn cs_heading_color">
                  <span>Learn More</span>
                  <span>
                  <i className="bi bi-arrow-right"></i>
                  </span>
                  </Link>
                </div>
              </article>
            </div>
             ))}
             </Slider>



          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Blog1;