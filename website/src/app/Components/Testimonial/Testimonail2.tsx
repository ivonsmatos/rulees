"use client"
import Image from "next/image";
import { useRef } from "react";
import Slider from "react-slick";

const Testimonail2 = () => {

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
    
      const previous = () => {
        sliderRef.current.slickPrev();
      }; 
        
       const bgImage = '/assets/img/testimonial-bg-1.svg';

        const testimonialContent = [
            {img:'/assets/img/rulees/person-3.jpg', subtitle:'Head de Produto · SaaS B2B', title:'Mariana Costa', content:'Antes, metade das regras de negócio ficava na cabeça de alguém. Com o Rulees, cada decisão da reunião vira uma regra com fonte e dono. Nosso retrabalho com requisito ambíguo despencou — e o time de dev confia no que recebe.'},
            {img:'/assets/img/rulees/person-2.jpg', subtitle:'CTO · Software House', title:'Rafael Andrade', content:'Atendemos vários clientes ao mesmo tempo e rastreabilidade é tudo. O Rules Ledger nos dá a evidência de onde cada requisito veio. Levar da reunião ao backlog no Jira virou questão de minutos, não de dias.'},
          ];


    return (
 <section className="cs_slider cs_style_1 cs_slider_gap_30 cs_bg_filed cs_radius_50_50 cs_mt_90 position-relative z-1" style={{ backgroundImage: `url(${bgImage})`}} >
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_type_1 cs_mb_60">
          <div className="cs_section_heading_left">
            <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
              <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
              <span>Depoimentos</span>
              <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
            </div>
            <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow fadeInUp">Quem usa, não volta <br/> para a ata de reunião</h2>
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
        <div className="cs_slider_container" data-autoplay="0" data-loop="1" data-speed="600" data-center="0" data-variable-width="0" data-slides-per-view="responsive" data-xs-slides="1" data-sm-slides="1" data-md-slides="1" data-lg-slides="1" data-add-slides="1">
          <div className="cs_slider_wrapper">
            <Slider ref={sliderRef} {...settings}>
            {testimonialContent.map((item, i) => (
            <div key={i} className="cs_slide">
              <div className="cs_testimonial cs_style_3 cs_white_bg cs_radius_20 position-relative">
                <div className="cs_testimonial_thumbnail">
                  <Image src={item.img} alt="img" width={312} height={449}   /> 
                </div>
                <div className="cs_testimonial_info">
                  <div className="cs_rating cs_mb_27" data-rating="5">
                    <div className="cs_rating_percentage"></div>
                  </div>
                  <blockquote>{item.content}</blockquote>
                  <div className="cs_avatar cs_style_1">
                    <div className="cs_avatar_info">
                      <h3 className="cs_fs_24 cs_semibold mb-0">{item.title}</h3>
                      <p className="cs_fs_14 mb-0">{item.subtitle}</p>
                    </div>
                  </div>
                  <div className="cs_quote_icon position-absolute">
                    <Image src="/assets/img/icons/qote-2.svg" alt="img" width={84} height={60}   /> 
                  </div>
                </div>
              </div>
            </div> 
              ))}
            </Slider>          

          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="cs_height_90 cs_height_lg_90"></div>
    </section>
    );
};

export default Testimonail2;