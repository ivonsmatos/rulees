import Image from "next/image";
import Link from "next/link";

const ProjectDetails = () => {
    return (
<section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_project_details">
          <div className="cs_banner cs_radius_50">
            <Image src="/assets/img/project-img-9.jpg" alt="img" width={1296} height={621}   />
          </div>
          <div className="row cs_gap_y_30">
            <div className="col-lg-4 order-lg-2">
              <div className="cs_project_info_wrapper cs_radius_15">
                <div className="cs_project_info_inner cs_white_bg cs_radius_15">
                  <h3 className="cs_fs_22 cs_bold cs_mb_22">Project Info: </h3>
                  <ul className="cs_project_info_list cs_mp_0">
                    <li>
                      <span className="cs_medium">Client:</span>
                      <span className="cs_medium cs_heading_color">Ralph Edwards</span>
                    </li>
                    <li>
                      <span className="cs_medium">Category:</span>
                      <span className="cs_medium cs_heading_color">App Landing</span>
                    </li>
                    <li>
                      <span className="cs_medium">Location:</span>
                      <span className="cs_medium cs_heading_color">London</span>
                    </li>
                    <li>
                      <span className="cs_medium">Share:</span>
                      <div className="cs_social_links cs_style_2 cs_heading_color">
                        <a href="#" aria-label="Social link"><i className="bi bi-facebook"></i></a>
                        <a href="#" aria-label="Social link"><i className="bi bi-twitter-x"></i></a>           
                        <a href="#" aria-label="Social link"><i className="bi bi-linkedin"></i></a>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div className="col-lg-8 order-lg-1">
              <div className="cs_project_desc">
                <h2>Interactive Design</h2>
                <p>Our UI/UX design services are crafted to elevate your digital presence with precision and creativity. We begin by understanding your goals and your audience, ensuring that every design decision aligns with your brand’s vision. Our approach integrates user research, wireframing, and prototyping to create intuitive and engaging interfaces.
                </p>
                <p>We focus on delivering seamless user experiences that drive engagement and satisfaction. From concept to launch, our team is dedicated to design solutions that are not only visually appealing but also functionally robust. We continuously test and refine our designs to meet the highest standards of usability.</p>
              </div>
            </div>
          </div>
          <h2>Challenges:</h2>
          <p>Nam posuere mauris enim, quis pretium elit placerat id  Fusce egestas nisi vel ipsum vehicula facilisis In pulvinar imperdiet venenatis  className aptent taciti sociosqu ad litora torent per conubia nostra, per inceptos himenaeos. Donec eu pulvinar lorem. Etiam vestibulum ligula quis nisl feugiat, consectetur placerat augue vestibulum  Nulla aliquam elit eu diam pharetra.Nam posuere mauris enim,</p>
          <ul>
            <li>
              <b>Inefficient Workflow:</b>
              The client faced significant delays due to manual processes and disjointed tools
            </li>
            <li>
              <b>Poor Collaboration:</b>
              Remote teams found it challenging to communicate and collaborate effectively
            </li>
            <li>
              <b>Data Silos:</b>
              Critical data was fragmented across multiple systems, making it difficult to gain insights.
            </li>
          </ul>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="cs_projects_wrapper">
        <div className="container">
            <div className="row cs_row_gap_30 cs_gap_y_30 justify-content-center">
                
                <div className="col-lg-4 cs_isotop_item">
                    <div className="cs_project_item cs_radius_10 position-relative">
                      <Image src="/assets/img/project-img-5.jpg" alt="img" width={412} height={437}   />
                    <div className="cs_project_info cs_radius_5 position-absolute">
                        <h3 className="cs_fs_24 cs_semibold cs_mb_6"><Link href="/project/project-details">Personal Brand Design</Link></h3>
                        <Link href="/project/project-details" className="cs_project_btn cs_fs_18 cs_theme_color_2">View Project</Link>
                    </div>
                    </div>
                </div>
                <div className="col-lg-4 cs_isotop_item">
                    <div className="cs_project_item cs_radius_10 position-relative">
                      <Image src="/assets/img/project-img-6.jpg" alt="img" width={412} height={437}   />
                    <div className="cs_project_info cs_radius_5 position-absolute">
                        <h3 className="cs_fs_24 cs_semibold cs_mb_6"><Link href="/project/project-details">Blog Webpage Design</Link></h3>
                        <Link href="/project/project-details" className="cs_project_btn cs_fs_18 cs_theme_color_2">View Project</Link>
                    </div>
                    </div>
                </div>
                <div className="col-lg-4 cs_isotop_item">
                    <div className="cs_project_item cs_radius_10 position-relative">
                      <Image src="/assets/img/project-img-7.jpg" alt="img" width={412} height={437}   />
                    <div className="cs_project_info cs_radius_5 position-absolute">
                        <h3 className="cs_fs_24 cs_semibold cs_mb_6"><Link href="/project/project-details">Brand Promoting</Link></h3>
                        <Link href="/project/project-details" className="cs_project_btn cs_fs_18 cs_theme_color_2">View Project</Link>
                    </div>
                    </div>
                </div>

            </div>

        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default ProjectDetails;