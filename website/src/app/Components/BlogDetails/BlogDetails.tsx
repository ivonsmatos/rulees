import Image from "next/image";
import Link from "next/link";

const BlogDetails = () => {
    return (
 <section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="row cs_row_gap_30 cs_gap_y_60">
          <aside className="col-xl-4 col-lg-5">
            <div className="cs_sidebar cs_style_1 cs_type_1">
              <div className="cs_sidebar_widget cs_gray_bg cs_radius_10">
                <h3 className="cs_sidebar_widget_title cs_fs_22 cs_semibold cs_mb_22">Search</h3>
                <form action="#" className="cs_search cs_white_bg position-relative">
                  <input type="text" placeholder="Search here" />
                  <button className="cs_search_button cs_center cs_blue_bg cs_white_color">
                  <i className="bi bi-search"></i></button>
                </form>
              </div>
              <div className="cs_sidebar_widget cs_gray_bg cs_radius_10">
                <h3 className="cs_sidebar_widget_title cs_fs_22 cs_semibold cs_mb_22">Categories</h3>
                <ul className="cs_service_category_list cs_heading_color cs_heading_font cs_mp_0">
                  <li><a href="#"><span>Technology</span><span>(7)</span></a>
                  </li>
                  <li><a href="#"><span>Business</span><span>(4)</span></a>
                  </li>
                  <li><a href="#"><span>Apps Development</span><span>(5)</span></a>
                  </li>
                  <li><a href="#"><span>Social Marketing</span><span>(3)</span></a>
                  </li>
                  <li><a href="#"><span>System</span><span>(6)</span></a>
                  </li>
                </ul>
              </div>
              <div className="cs_sidebar_widget cs_gray_bg cs_radius_10">
                <h3 className="cs_sidebar_widget_title cs_fs_22 cs_semibold cs_mb_22">Recent Posts</h3>
                <div className="cs_recent_post_wrapper">
                  <div className="cs_recent_post">
                    <a aria-label="Click to read post" className="cs_recent_post_thumb cs_radius_10" href="/blog-details">
                    <Image src="/assets/img/post-img-13.jpg" alt="img" width={80} height={81}   /> 
                    </a>
                    <div className="cs_recent_post_right">
                      <div className="cs_post_meta cs_fs_14 cs_mb_9">
                        <i className="fa-solid fa-calendar-alt"></i>17 Mar, 2024
                      </div>
                      <h3 className="cs_fs_16 cs_bold mb-0">
                        <Link href="/blog/blog-details" aria-label="Reading details post link">There are many vario ns of passages of</Link>
                      </h3>
                    </div>
                  </div>
                  <div className="cs_recent_post">
                    <a aria-label="Click to read post" className="cs_recent_post_thumb cs_radius_10" href="/blog-details">
                    <Image src="/assets/img/post-img-14.jpg" alt="img" width={80} height={81}   /> 
                    </a>
                    <div className="cs_recent_post_right">
                      <div className="cs_post_meta cs_fs_14 cs_mb_9">
                        <i className="fa-solid fa-calendar-alt"></i>14 Dec, 2024
                      </div>
                      <h3 className="cs_fs_16 cs_bold mb-0">
                        <Link href="/blog/blog-details" aria-label="Reading details post link">There are many vario ns of passages of</Link>
                      </h3>
                    </div>
                  </div>
                  <div className="cs_recent_post">
                    <a aria-label="Click to read post" className="cs_recent_post_thumb cs_radius_10" href="/blog-details">
                    <Image src="/assets/img/post-img-15.jpg" alt="img" width={80} height={81}   /> 
                    </a>
                    <div className="cs_recent_post_right">
                      <div className="cs_post_meta cs_fs_14 cs_mb_9">
                        <i className="fa-solid fa-calendar-alt"></i>27 Feb, 2024
                      </div>
                      <h3 className="cs_fs_16 cs_bold mb-0">
                         <Link href="/blog/blog-details" aria-label="Reading details post link">There are many vario ns of passages of</Link>
                      </h3>
                    </div>
                  </div>
                </div>
              </div>
              <div className="cs_sidebar_widget cs_gray_bg cs_radius_10">
                <div className="cs_sidebar_tags">
                  <h3 className="cs_sidebar_widget_title cs_fs_22 cs_semibold cs_mb_22">Tags</h3>
                  <div className="cs_tags_links cs_fs_14 cs_heading_color cs_heading_font">
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Security</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Business</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Digital</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Technology</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Change</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Video</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>UI/UX Design</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg cs_radius_4"><span>Startup</span></a>
                  </div>
                </div>
              </div>
            </div>
          </aside>
          <div className="col-xl-8 col-lg-7">
            <div className="cs_post_details">
              <div className="cs_post_banner cs_radius_10 cs_mb_40 position-relative">
                <Image src="/assets/img/post-img-10.jpg" alt="img" width={812} height={485}   /> 
                <div className="cs_posted_by cs_center_column cs_heading_font cs_radius_8 position-absolute">
                  <span className="cs_fs_24 cs_bold cs_white_color">20</span>
                  <span className="cs_fs_12 cs_white_color">Feb</span>
                </div>
              </div>
              <div className="cs_post_meta_wrapper cs_mb_17">
                <div className="cs_post_meta">
                  <span className="cs_blue_color"><i className="bi bi-person"></i></span>
                  <span className="cs_heading_color">Admin</span>
                </div>
                <div className="cs_post_meta">
                  <span className="cs_blue_color"><i className="bi bi-chat"></i></span>
                  <span className="cs_heading_color">2 Comments</span>
                </div>
                <div className="cs_post_meta">
                  <span className="cs_blue_color"><i className="bi bi-bookmark"></i></span>
                  <span className="cs_heading_color">Technology</span>
                </div>
              </div>
              <h2>Choose The Best Service Company in the City.</h2>
              <p>Consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore of magna aliqua. Ut enim ad minim veniam, made of owl the quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea dolor commodo consequat. Duis aute irure and dolor in reprehenderit.</p>
              <p>The is ipsum dolor sit amet consectetur adipiscing elit. Fusce eleifend porta arcu In hac habitasse the is platea augue thelorem turpoi dictumst. In lacus libero faucibus at malesuada sagittis placerat eros sed istincidunt augue ac ante rutrum sed the is sodales augue consequat.</p>
              <div className="row cs_row_gap_30 cs_gap_y_30 cs_mb_30 cs_mb_40">
                <div className="col-md-6">
                  <Image src="/assets/img/post-img-11.jpg" alt="img" width={391} height={284}   /> 
                </div>
                <div className="col-md-6">
                  <Image src="/assets/img/post-img-12.jpg" alt="img" width={391} height={284}   /> 
                </div>
              </div>
              <p>The is ipsum dolor sit amet consectetur adipiscing elit. Fusce eleifend porta arcu In hac habitasse the is platea augue thelorem turpoi dictumst. In lacus libero faucibus at malesuada sagittis placerat eros sed istincidunt augue ac ante rutrum sed the is sodales augue consequat.</p>
              <div className="cs_quote_wrapper position-relative">
                <blockquote>            
                  Pellentesque sollicitudin congue dolor non aliquam. Morbi volutpat, nisi vel ultricies urnacondimentum, sapien neque lobortis tortor, quis efficitur mi ipsum eu metus. Praesent eleifend orci sit amet est vehicula.
                </blockquote>
                <Image src="/assets/img/icons/qote-3.svg" alt="img" width={36} height={36}   /> 
              </div>
              <p>Consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore of magna aliqua. Ut enim ad minim veniam, made of owl the quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea dolor commodo consequat. Duis aute irure and dolor in reprehenderit.</p>
              <div className="cs_post_share_wrapper">
                <div className="cs_post_tags cs_style_1">
                  <h3 className="cs_fs_16 cs_semibold">Tags:</h3>
                  <div className="cs_tags_links cs_fs_14 cs_heading_color cs_heading_font">
                    <a href="#" className="cs_tag_link cs_white_bg"><span>Security</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg"><span>UI/UX Desing</span></a>
                    <a href="#" className="cs_tag_link cs_white_bg"><span>Digital</span></a>
                  </div>
                </div>
                <div className="cs_post_socials">
                  <h3 className="cs_fs_16 cs_semibold">Share:</h3>
                  <div className="cs_social_links cs_style_2">
                    <a href="#"><i className="bi bi-facebook"></i></a>
                    <a href="#"><i className="bi bi-twitter-x"></i></a>
                    <a href="#"><i className="bi bi-linkedin"></i></a>
                    <a href="#"><i className="bi bi-instagram"></i></a>
                  </div>
                </div>
              </div>
            </div>
            <div className="cs_height_70 cs_height_lg_60"></div>
            <div className="cs_comments_area">
              <h2 className="cs_fs_24 cs_mb_30">02 Comments</h2>
              <ul className="cs_comment_list cs_heading_font cs_mp_0">
                <li className="cs_comment_body position-relative">
                  <div className="cs_comment_thumbnail cs_radius_15">
                    <Image src="/assets/img/avatar-7.jpg" alt="img" width={96} height={96}   /> 
                  </div>
                  <div className="cs_comment_info">
                    <div className="cs_client_info cs_mb_18">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Leslie Alexander</h3>
                      <p className="cs_fs_14 cs_medium mb-0">February 10, 2025 at 2:37 pm</p>
                    </div>
                    <p className="mb-0">Neque porro est qui dolorem ipsum quia quaed inventor veritatis et quasi architecto var sed efficitur turpis gilla sed sit amet finibus eros.</p>
                    <button aria-label="Reply button" className="cs_reply_btn cs_fs_14 cs_heading_font cs_white_color">Reply</button>
                  </div>
                </li>
                <li className="cs_comment_body position-relative">
                  <div className="cs_comment_thumbnail cs_radius_15">
                    <Image src="/assets/img/avatar-8.jpg" alt="img" width={96} height={96}   /> 
                  </div>
                  <div className="cs_comment_info">
                    <div className="cs_client_info cs_mb_18">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Ralph Edwards</h3>
                      <p className="cs_fs_14 cs_medium mb-0">February 10, 2025 at 2:37 pm</p>
                    </div>
                    <p className="mb-0">Neque porro est qui dolorem ipsum quia quaed inventor veritatis et quasi architecto var sed efficitur turpis gilla sed sit amet finibus eros. </p>
                    <button aria-label="Reply button" className="cs_reply_btn cs_fs_14 cs_heading_font cs_white_color">Reply</button>
                  </div>
                </li>
              </ul>
              <div className="cs_height_60 cs_height_lg_50"></div>
              <div className="cs_comment_form_wrapper cs_style_1">
                <h3 className="cs_fs_24 cs_mb_22">Leave a Comment</h3>
                <form className="cs_comment_form row cs_row_gap_30 cs_gap_y_30">
                  <div className="col-sm-6">
                    <label htmlFor="name">Your Name*</label>
                    <input type="text" name="name" id="name" placeholder="Your Name" className="cs_form_field cs_radius_8" />
                  </div>
                  <div className="col-sm-6">
                    <label htmlFor="email">Your Email*</label>
                    <input type="email" name="email" id="email" placeholder="Email Address" className="cs_form_field cs_radius_8" />
                  </div>
                  <div className="col-sm-12">
                    <label htmlFor="message">Message*</label>
                    <textarea name="comment" rows={6} id="message" placeholder="Enter Your Comments" className="cs_form_field cs_radius_8"></textarea>
                  </div>
                  <div className="col-sm-12">
                    <button type="submit" aria-label="Post comment button" className="cs_btn cs_style_1 cs_bg_1 cs_heading_font cs_white_color">
                    <span>Post a Comment</span>
                    <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default BlogDetails;