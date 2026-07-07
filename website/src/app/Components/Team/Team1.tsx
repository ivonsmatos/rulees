import Image from "next/image";
import Link from "next/link";

const Team1 = () => {

    const teamContent = [
        {img:'/assets/img/team-img-1.jpg', name:'Esther howard', content:'co-Founder',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-2.jpg', name:'Leslie Alexander', content:'co-Founder',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-3.jpg', name:'Theresa Web', content:'HR manager',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
      ];

    return (
<section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_center_column cs_mb_47 text-center position-relative z-1">
          <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
            <span>Our Team</span>
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
          </div>
          <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0">Our Experts Team Member</h2>
        </div>
        <div className="row cs_row_gap_30 cs_gap_y_30 justify-content-center">

        {teamContent.map((item, i) => (
          <div key={i} className="col-lg-4">
            <div className="cs_team cs_style_1">
              <Link href="/team/team-details" className="cs_team_thumbnail cs_radius_100 cs_center position-relative z-1">
              <Image src={item.img} alt="img" width={300} height={300}   />
              </Link>
              <div className="cs_team_info cs_radius_30 cs_white_bg cs_center_column text-center">
                <h3 className="cs_team_title cs_fs_24 cs_semibold cs_mb_4"><Link href="/team/team-details">{item.name}</Link></h3>
                <p className="cs_fs_18 cs_heading_color cs_mb_12">{item.content}</p>
                <div className="cs_social_links cs_style_1">
                    <a href={item.facebook}><i className="bi bi-facebook"></i></a>
                    <a href={item.twitter}><i className="bi bi-twitter-x"></i></a>
                    <a href={item.linkedin}> <i className="bi bi-linkedin"></i></a>
                    <a href={item.instagram}><i className="bi bi-instagram"></i></a>
                </div>
              </div>
            </div>
          </div>
          ))}

        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Team1;