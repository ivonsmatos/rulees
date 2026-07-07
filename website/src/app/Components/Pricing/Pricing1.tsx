"use client"
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

const Pricing1 = () => {

  const [billingType, setBillingType] = useState('monthly');

  const handleToggle = (value) => {
    setBillingType(value);
  };

  return (
    <section className="position-relative overflow-hidden">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_center_column cs_mb_60 text-center position-relative z-1">
          <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
            <span>Our Pricing</span>
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
          </div>
          <h2 className="cs_section_title cs_fs_48 cs_semibold cs_mb_20 text-capitalize wow fadeInUp">
            Choose A Plan for more <br /> advanced business
          </h2>
          <div className="cs_center">
            <ul className="cs_pricing_control cs_center cs_mp_0 cs_fs_14 cs_bold text-uppercase position-relative">
              <li className={billingType === 'monthly' ? 'active' : ''}>
                <a href="#monthly" onClick={(e) => { e.preventDefault(); handleToggle('monthly'); }}>
                  Monthly
                </a>
              </li>
              <li className={billingType === 'yearly' ? 'active' : ''}>
                <a href="#yearly" onClick={(e) => { e.preventDefault(); handleToggle('yearly'); }}>
                  Yearly
                </a>
                <div className="cs_offer_info cs_fs_20 cs_heading_color cs_heading_font cs_normal position-absolute">
                  <span>Save 20%</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <div className="row cs_row_gap_30 cs_gap_y_30 position-relative z-1">
          {[{
            title: 'Starter Plan',
            monthly: '49',
            yearly: '89',
            popular: false
          }, {
            title: 'Standard Plan',
            monthly: '149',
            yearly: '189',
            popular: true
          }].map((plan, index) => (
            <div className="col-lg-6" key={index}>
              <div className={`cs_pricing_table cs_style_2 cs_white_bg cs_radius_20 position-relative${plan.popular ? ' active' : ''}`}>
                <div className="cs_pricing_table_heading cs_mb_18 position-relative z-1">
                  <div>
                    <h2 className="cs_plan_title cs_fs_24 cs_semibold cs_mb_7">{plan.title}</h2>
                    <p className="mb-0">Advanced features & reporting</p>
                  </div>
                  <div className="cs_price cs_fs_74 cs_semibold cs_heading_color cs_heading_font">
                    ${billingType === 'monthly' ? plan.monthly : plan.yearly}
                  </div>
                </div>

                {plan.popular && (
                  <div className="cs_pricing_badge cs_heading_color cs_medium cs_theme_bg_4 text-center">
                    Most Popular
                  </div>
                )}

                <div className="cs_separator cs_mb_24"></div>
                <div className="cs_feature_list_wrapper cs_mb_28">
                  <div>
                    <h3 className="cs_feature_title cs_fs_24 cs_normal cs_mb_16">Account & Support</h3>
                    <ul className="cs_pricing_feature_list cs_mp_0">
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Unlimited users</li>
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Unlimited connectors</li>
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> CRM onboarding session</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="cs_feature_title cs_fs_24 cs_normal cs_mb_16">Platform Access</h3>
                    <ul className="cs_pricing_feature_list cs_mp_0">
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Accountant access</li>
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Limited invoicing</li>
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Custom number of users</li>
                      <li><span className="cs_feature_icon"><i className="bi bi-check-circle-fill"></i></span> Up to 5 projects collaborations</li>
                    </ul>
                  </div>
                </div>
                <Link href="/contact" aria-label="Buy service button" className="cs_btn cs_style_1 cs_center cs_fs_14 cs_bold cs_heading_color text-uppercase text-center">
                  <span>GET STARTED NOW</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="cs_pricing_shape_3 position-absolute">
          <Image src="/assets/img/trash-group-2.svg" alt="img" width={98} height={98}   /> 
        </div>
        <div className="cs_pricing_shape_4 position-absolute">
          <Image src="/assets/img/vector-8.svg" alt="img" width={35} height={37}   /> 
        </div>
        <div className="cs_pricing_shape_5 position-absolute">
          <Image src="/assets/img/vector-9.svg" alt="img" width={37} height={37}   /> 
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
  


    );
};

export default Pricing1;