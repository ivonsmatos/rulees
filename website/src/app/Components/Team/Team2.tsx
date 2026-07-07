import Image from "next/image";
import Link from "next/link";

const Team2 = () => {

    const teamContent = [
        {img:'/assets/img/team-img-1.jpg', name:'Esther howard', content:'co-Founder',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-2.jpg', name:'Leslie Alexander', content:'co-Founder',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-3.jpg', name:'Theresa Web', content:'HR manager',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-4.jpg', name:'Jacob Jones', content:'HR manager',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-5.jpg', name:'Annette Black', content:'co-Founder',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
        {img:'/assets/img/team-img-6.jpg', name:'Dianne Russell', content:'HR manager',instagram:'#',facebook:'#',twitter:'#',linkedin:'#'},
      ];

    return (
<section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">

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

export default Team2;