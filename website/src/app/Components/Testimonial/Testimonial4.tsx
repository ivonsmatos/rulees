"use client"
import Image from "next/image";
import { useRef } from "react";
import Slider from "react-slick";

const Testimonial4 = () => {

        const settings = {
        dots: false,
        infinite: true,
        speed: 2000,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        swipeToSlide: true,
        autoplay: true,
        autoplaySpeed: 4000,        
        responsive: [
          {
            breakpoint: 1399,
            settings: {
              slidesToShow: 1,
            }
          },
          {
            breakpoint: 1199,
            settings: {
              slidesToShow: 1,
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
    
    const testimonialContent = [
        {img:'/assets/img/avatar-5.jpg', subtitle:'Marketing Manager', title:'Juliana Rose', content:'This is why having reviews and client testimonials is so important for your business. So, in this article,  go over some client testimonial examples you should be aware of and how you can go about gathering those testimonials for yourself. This is why having reviews and client testimonials is so important for your business. So, in this article, we’ll go over some client testimonial'},             
        {img:'/assets/img/avatar-6.jpg', subtitle:'UI/UX Designer', title:'Anjelina Rose', content:'This is why having reviews and client testimonials is so important for your business. So, in this article,  go over some client testimonial examples you should be aware of and how you can go about gathering those testimonials for yourself. This is why having reviews and client testimonials is so important for your business. So, in this article, we’ll go over some client testimonial'},             
      ]; 


    return (
<section className="cs_slider cs_style_1 cs_slider_gap_30 position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_testimonial_slider_wrapper cs_radius_20 position-relative">
          <div className="cs_section_heading cs_style_1 cs_mb_10">
            <h2 className="cs_section_title cs_fs_24 cs_normal mb-0">Clients Feedback</h2>
          </div>
          <div className="cs_slider_container" data-autoplay="0" data-loop="1" data-speed="600" data-center="0" data-variable-width="0" data-slides-per-view="responsive" data-xs-slides="1" data-sm-slides="1" data-md-slides="1" data-lg-slides="1" data-add-slides="1">
            <div className="cs_slider_wrapper">

            <Slider ref={sliderRef} {...settings}>
            {testimonialContent.map((item, i) => (
              <div key={i} className="cs_slide">
                <div className="cs_testimonial cs_style_2">
                  <div className="cs_testimonial_heading cs_mb_10">
                    <span className="cs_quote_icon cs_center cs_white_bg cs_radius_100">
                   <Image src="/assets/img/icons/qote.svg" alt="img" width={96} height={96}   />
                    </span>
                    <div className="cs_rating" data-rating="5">
                      <div className="cs_rating_percentage"></div>
                    </div>
                  </div>
                  <blockquote>{item.content}</blockquote>
                  <div className="cs_avatar cs_style_1">
                    <span className="cs_avatar_icon cs_center cs_radius_100">
                    <Image src={item.img} alt="img" width={80} height={80}   />
                    </span>
                    <div className="cs_avatar_info">
                      <h3 className="cs_fs_20 cs_semibold mb-0">{item.title}</h3>
                      <p className="cs_fs_14 mb-0">{item.subtitle}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            </Slider>

            </div>
            <div className="cs_slider_arrows cs_style_1">
              <div onClick={next} className="cs_right_arrow rounded-circle cs_center cs_white_bg cs_theme_color_2 slick-arrow">
                <i className="bi bi-chevron-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    );
};

export default Testimonial4;