import Image from 'next/image';
import Link from 'next/link';
import React from 'react';

const Toolset2 = () => {

        const brandContent = [
        {img:'/assets/img/rulees/jira.svg', title:'Jira'},
        {img:'/assets/img/rulees/confluence.svg', title:'Confluence'},
        {img:'/assets/img/rulees/azuredevops.svg', title:'Azure DevOps'},
      ];

    return (
 <section className="cs_gray_bg_2 cs_radius_50_50 cs_mt_90 position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_toolset_content cs_type_1 cs_center_column">
          <div className="cs_toolset_logos">
            {brandContent.map((item, i) => (
            <div key={i} className="cs_iconbox cs_style_3 cs_center_column cs_white_bg cs_radius_16 text-center">
              <span className="cs_iconbox_icon cs_mb_14">
              <img src={item.img} alt={`Integração com ${item.title}`} />
              </span>
              <p className="cs_medium mb-0">{item.title}</p>
            </div>
            ))}

          </div>
          <div className="cs_toolset_text text-center">
            <div className="cs_section_heading cs_style_1 cs_mb_37">
              <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
                <span>Integrações</span>
                <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
              </div>
              <h2 className="cs_section_title cs_fs_48 cs_semibold mb-0 wow zoomIn">Conectado às ferramentas que seu time já usa</h2>
            </div>
            <Link href="/integrations" aria-label="Ver todas as integrações" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
            <span>Ver todas as integrações</span>
            <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
            </Link>
          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="cs_height_90 cs_height_lg_90"></div>
    </section>
    );
};

export default Toolset2;