import ServiceCard1 from '../Card/ServiceCard1';
import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

const Services1 = () => {
      const bgImage = '/assets/img/feature-item-bg.svg';
    return (
 <section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_mb_47 cs_center_column text-center position-relative z-1">
          <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
            <span>Awesome Feature</span>
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
          </div>
          <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow fadeInUp">Powerful Features to Elevate <br/> Your Workflow</h2>
        </div>
        <div className="cs_features_items_wrapper position-relative z-1">
          <div className="cs_feature_item cs_radius_20 cs_bg_filed" style={{ backgroundImage: `url(${bgImage})`}} >
            <h3 className="cs_fs_36 cs_semibold cs_white_color cs_mb_40">See more and get visibility <br/> for your business</h3>
            <Link href="/contact" aria-label="Get started button" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
            <span>Get Started</span>
            <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
            </Link>
          </div>

          <ServiceCard1
            addclass="cs_bg_00"
            serviceicon="/assets/img/icons/code-icon.svg"
            title="Software Development"
            featureList={[
                "Security",
                "Agile Methodologies",
                "Clear Requirements",
                "Feedback &  Improvement"
            ]}
            btnname="Read More"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_1"
            serviceicon="/assets/img/icons/cloud-computing.svg"
            title="Cloud Computing Solutions"
            featureList={[
                "Security",
                "Agile Methodologies",
                "Clear Requirements",
                "Feedback &  Improvement"
            ]}
            btnname="Read More"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_2"
            serviceicon="/assets/img/icons/quality-assurance.svg"
            title="Quality Assurance"
            featureList={[
                "Security",
                "Agile Methodologies",
                "Clear Requirements",
                "Feedback &  Improvement"
            ]}
            btnname="Read More"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_3"
            serviceicon="/assets/img/icons/security.svg"
            title="Cybersecurity Services"
            featureList={[
                "Security",
                "Agile Methodologies",
                "Clear Requirements",
                "Feedback &  Improvement"
            ]}
            btnname="Read More"
            btnurl="/service/service-details"
          ></ServiceCard1>

        </div>
      </div>
      <div className="cs_feature_shape_1 position-absolute">
        <Image src="/assets/img/3d-shape.png" alt="img" width={97} height={104}   />
      </div>
      <div className="cs_feature_shape_2 position-absolute">
        <Image src="/assets/img/spring-shape.png" alt="img" width={88} height={88}   />
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Services1;