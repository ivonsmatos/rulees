import Image from "next/image";
import Link from "next/link";

const Blog4 = () => {

     const blogContent = [
        {img:'/assets/img/post-img-16.jpg', title:'Choose The Best Service Company in the City.', content:'Pellentesque egestas rutrum nibh facilisis ultrices. Phasellus in magna ut orci malesuada the sollicitudin. Aenean faucibus scelerisque convallis. Quisque interdum mauris id nunc molestie tincidunt erat gravida. Nullam dui libero, mollis ac quam et, venenatis.'},
        {img:'/assets/img/post-img-17.jpg', title:'Keep Your Business Ensure High Availability', content:'Pellentesque egestas rutrum nibh facilisis ultrices. Phasellus in magna ut orci malesuada the sollicitudin. Aenean faucibus scelerisque convallis. Quisque interdum mauris id nunc molestie tincidunt erat gravida. Nullam dui libero, mollis ac quam et, venenatis.'},
        {img:'/assets/img/post-img-18.jpg', title:'Tackling the Changes of Retell Industry', content:'Pellentesque egestas rutrum nibh facilisis ultrices. Phasellus in magna ut orci malesuada the sollicitudin. Aenean faucibus scelerisque convallis. Quisque interdum mauris id nunc molestie tincidunt erat gravida. Nullam dui libero, mollis ac quam et, venenatis.'},
      ];   


    return (
        <div>
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
          <div className="cs_posts_wrapper">
            {blogContent.map((item, i) => (
            <article key={i} className="cs_post cs_style_1 cs_type_2 cs_radius_16">
              <Link href="/blog/blog-details" aria-label="Reading details post link" className="cs_post_thumbnail cs_radius_10 cs_mb_28 position-relative overflow-hidden">
                <Image src={item.img} alt="img" width={750} height={454}   /> 
                <div className="cs_posted_by cs_center_column cs_heading_font cs_white_color cs_radius_8 position-absolute">
                  <span className="cs_fs_24 cs_bold cs_mb_2">15</span>
                  <span className="cs_fs_14">Feb</span>
                </div>
              </Link>
              <div className="cs_post_content">
                <div className="cs_post_meta_wrapper cs_mb_10">
                  <div className="cs_post_meta cs_fs_14">
                    <span><i className="bi bi-person"></i></span>
                    <span>By Admin</span>
                  </div>
                  <div className="cs_post_meta">
                    <span><i className="bi bi-chat"></i></span>
                    <span>0 Comments</span>
                  </div>
                </div>
                <h3 className="cs_post_title cs_fs_30 cs_semibold cs_mb_7"><Link href="/blog/blog-details" aria-label="Reading details post link">{item.title}</Link></h3>
                <p className="cs_post_subtitle cs_heading_font cs_mb_21">{item.content}</p>
                <Link href="/blog/blog-details" aria-label="Reading details post link" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_semibold cs_heading_font cs_white_color">
                <span>Read More</span>
                <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                </Link>
              </div>
            </article>
            ))}

            
          </div>

        </div>
      </div>
    </div>
    <div className="cs_height_120 cs_height_lg_80"></div>            
        </div>
    );
};

export default Blog4;