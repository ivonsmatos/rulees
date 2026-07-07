import Image from "next/image";

const TeamDetails = () => {
    return (
    <section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_team_details">
          <div className="cs_team_info_wrapper cs_gray_bg_2 cs_radius_50">
            <div className="row cs_gap_y_40">
              <div className="col-lg-5">
                <div className="cs_team_thumbnail cs_radius_30">
                  <Image src="/assets/img/team-img-7.jpg" alt="img" width={493} height={478}   />
                </div>
              </div>
              <div className="col-lg-7">
                <div className="cs_team_info">
                  <div className="cs_team_header cs_mb_26">
                    <div className="cs_team_heading">
                      <h3 className="cs_fs_48 cs_semibold">Olivia Martinez</h3>
                      <p className="mb-0">Gemini market</p>
                    </div>
                    <div className="cs_social_links cs_style_1">
                      <a href="#" className="cs_center cs_radius_50">
                     <i className="bi bi-facebook"></i>
                      </a>
                      <a href="#" className="cs_center cs_radius_50">
                      <i className="bi bi-twitter-x"></i>
                      </a>
                      <a href="#" className="cs_center cs_radius_50">
                      <i className="bi bi-linkedin"></i>
                      </a>
                      <a href="#" className="cs_center cs_radius_50">
                      <i className="bi bi-youtube"></i>
                      </a>
                    </div>
                  </div>
                  <p>Our UI/UX design services are crafted to elevate your digital presence with precision and creativity. We begin by understanding your goals and your audience, ensuring that every design decision </p>
                  <p>Aligns with your brand’s vision. Our approach integrates user research, wireframing, and prototyping to create intuitive and engaging interfaces.</p>
                  <ul className="cs_contact_list cs_mp_0">
                    <li>
                      <span className="cs_contact_icon cs_center cs_radius_100 cs_white_bg"><i className="bi bi-telephone-fill"></i></span>
                      <a href="tel:+9156980036420">+91 5698 0036 420</a>
                    </li>
                    <li>
                      <span className="cs_contact_icon cs_center cs_radius_100 cs_white_bg"><i className="bi bi-envelope-fill"></i></span>
                      <a href="mailto:info@Reiatix.com">info@Reiatix.com</a>
                    </li>
                    <li>
                      <span className="cs_contact_icon cs_center cs_radius_100 cs_white_bg"><i className="bi bi-geo-alt-fill"></i></span>
                      <span className="mb-0">26 Manor St, Braintree UK</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div className="cs_team_about">
            <h2>About Olivia Martinez</h2>
            <p>Our UI/UX design services are crafted to elevate your digital presence with precision and creativity. We begin by understanding your goals and your audience, ensuring that every design decision aligns with your brand’s vision. Our approach integrates user research, wireframing, and prototyping to create intuitive and engaging interfaces.
            </p>
            <p>We focus on delivering seamless user experiences that drive engagement and satisfaction. From concept to launch, our team is dedicated to design solutions that are not only visually appealing but also functionally robust. We continuously test and refine our designs to meet the highest standards of usability.</p>
            <ul>
              <li>consectetur placerat augue vestibulum</li>
              <li>Mauris tincidunt a eget facilisis  Quisque </li>
              <li>Lorem ipsum dolor sit amet, consectetur </li>
            </ul>
            <p>Nam posuere mauris enim, quis pretium elit placerat id  Fusce egestas nisi vel ipsum vehicula facilisis In pulvinar imperdiet venenatis  className aptent taciti sociosqu ad litora torent per conubia nostra, per inceptos himenaeos. Donec eu pulvinar lorem. Etiam vestibulum ligula quis nisl feugiat, consectetur placerat augue vestibulum  Nulla aliquam elit eu diam pharetra.Nam posuere mauris enim,</p>
          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default TeamDetails;