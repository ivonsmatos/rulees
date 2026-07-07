import Image from 'next/image';
import Link from 'next/link';
import React from 'react';

const Pricing3 = () => {
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
          <h2 className="cs_section_title cs_fs_48 cs_semibold cs_mb_20 text-capitalize wow fadeInUp">Starter Plan For Everyone</h2>
          <p className="mb-0">All the generators on the Internet tend to repeat predefined chunks as necessary, making this <br/> the first true generator on the Internet.</p>
        </div>
        <div className="row cs_row_gap_30 cs_gap_y_30 align-items-end position-relative z-1">
          <div className="col-lg-4">
            <div className="cs_pricing_table cs_style_1 cs_gray_bg_2 cs_radius_30">
              <div className="cs_pricing_table_heading cs_mb_3">
                <h2 className="cs_plan_title cs_fs_24 cs_semibold mb-0">Basic Plan</h2>
                <span className="cs_plan_icon">
                  <Image src="/assets/img/icons/free.svg" alt="img" width={48} height={50}   />   
                </span>
              </div>
              <div className="cs_pricing_info cs_mb_20">
                <div className="cs_price cs_fs_48 cs_semibold cs_heading_color cs_heading_font cs_mb_4">$0 <small>Per User/Month</small></div>
                <p className="mb-0">Get essential features to kickstart your journey to success</p>
              </div>
              <div className="cs_separator cs_mb_22"></div>
              <div className="cs_feature_wrapper cs_mb_30">
                <ul className="cs_pricing_feature_list cs_mp_0">
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Access to all basic features</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Basic reporting and analytics</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Up to 10 individual users</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Weekly meeting for teams</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Task management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Team management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Chat support</span>
                  </li>
                </ul>
              </div>
              <Link href="/contact" aria-label="Buy service button" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_heading_color text-uppercase">
              <span>Get Started</span>
              <span className="cs_btn_icon"><i className="fa-solid fa-arrow-right"></i></span>
              </Link>
            </div>
          </div>
          <div className="col-lg-4">
            <div className="cs_pricing_table cs_style_1 cs_gray_bg_2 cs_radius_30 position-relative cs_active">
              <div className="cs_pricing_table_shape position-absolute">
                <Image src="/assets/img/pricing-shape-1.svg" alt="img" width={410} height={688}   />   
              </div>
              <div className="cs_pricing_badge cs_accent_bg cs_medium cs_white_color text-center position-absolute">Most Popular</div>
              <div className="cs_pricing_table_heading cs_mb_3">
                <h2 className="cs_plan_title cs_fs_24 cs_semibold mb-0">Standard Plan</h2>
                <span className="cs_plan_icon">
                  <Image src="/assets/img/icons/dimond.svg" alt="img" width={62} height={52}   />   
                </span>
              </div>
              <div className="cs_pricing_info cs_mb_20">
                <div className="cs_price cs_fs_48 cs_semibold cs_heading_color cs_heading_font cs_mb_4">$39 <small>Per User/Month</small></div>
                <p className="mb-0">Get essential features to kickstart your journey to success</p>
              </div>
              <div className="cs_separator cs_mb_22"></div>
              <div className="cs_feature_wrapper cs_mb_30">
                <ul className="cs_pricing_feature_list cs_mp_0">
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Access to all basic features</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Basic reporting and analytics</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Up to 10 individual users</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Weekly meeting for teams</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Task management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Team management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title">Chat support</span>
                  </li>
                </ul>
              </div>
              <Link href="/contact" aria-label="Buy service button" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_heading_color text-uppercase">
              <span>Get Started</span>
              <span className="cs_btn_icon"><i className="fa-solid fa-arrow-right"></i></span>
              </Link>
            </div>
          </div>
          <div className="col-lg-4">
            <div className="cs_pricing_table cs_style_1 cs_gray_bg_2 cs_radius_30">
              <div className="cs_pricing_table_heading cs_mb_3">
                <h2 className="cs_plan_title cs_fs_24 cs_semibold mb-0">Business Plan</h2>
                <span className="cs_plan_icon">
                  <Image src="/assets/img/icons/crown.svg" alt="img" width={64} height={50}   />   
                </span>
              </div>
              <div className="cs_pricing_info cs_mb_20">
                <div className="cs_price cs_fs_48 cs_semibold cs_heading_color cs_heading_font cs_mb_4">$49 <small>Per User/Month</small></div>
                <p className="mb-0">Get essential features to kickstart your journey to success</p>
              </div>
              <div className="cs_separator cs_mb_22"></div>
              <div className="cs_feature_wrapper cs_mb_30">
                <ul className="cs_pricing_feature_list cs_mp_0">
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Access to all basic features</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Basic reporting and analytics</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Up to 10 individual users</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Weekly meeting for teams</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Task management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Team management</span>
                  </li>
                  <li>
                    <span className="cs_feature_icon cs_green_color">
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z" fill="currentColor"/>
                      </svg>
                    </span>
                    <span className="cs_feature_title cs_heading_color">Chat support</span>
                  </li>
                </ul>
              </div>
              <Link href="/contact" aria-label="Buy service button" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_heading_color text-uppercase">
              <span>Get Started</span>
              <span className="cs_btn_icon"><i className="fa-solid fa-arrow-right"></i></span>
              </Link>
            </div>
          </div>
        </div>
        <div className="cs_pricing_shape_2 position-absolute">
          <Image src="/assets/img/vector-6.svg" alt="img" width={1808} height={1093}   />   
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Pricing3;