import Image from 'next/image';
import React from 'react';

const Analysis1 = () => {
    return (
<section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_card cs_style_1 cs_type_3">
          <div className="row cs_gap_y_50 position-relative z-1">
            <div className="col-lg-6">
              <div className="cs_card_thumbnail position-relative">
                <Image src="/assets/img/dashboard.png" alt="img" width={631} height={461}   />
              </div>
            </div>
            <div className="col-lg-6">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_27">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
                    <span>Rastreabilidade & Evidência</span>
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInLeft">Da fala na reunião ao requisito, com evidência</h2>
                  <p className="cs_card_desc mb-0">Cada regra, decisão e dúvida fica ligada ao trecho exato da reunião que a originou. Acabou o “quem decidiu isso?”: a origem é auditável de ponta a ponta.</p>
                </div>
                <div className="cs_iconbox_wrapper_1">
                  <div className="cs_iconbox cs_style_1 cs_type_1">
                    <span className="cs_iconbox_icon cs_center cs_accent_bg">
                      <Image src="/assets/img/icons/advanced-tracking.svg" alt="img" width={51} height={50}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Matriz de rastreabilidade</h3>
                      <p className="mb-0">Origem, regra, decisão, história e critério conectados em um só lugar.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_1 cs_type_1">
                    <span className="cs_iconbox_icon cs_center cs_bg_1">
                      <Image src="/assets/img/icons/in-depth.svg" alt="img" width={39} height={50}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_20 cs_semibold cs_mb_1">Trilha de auditoria</h3>
                      <p className="mb-0">Quem aprovou, quando e com base em qual evidência — tudo registrado.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_star_shape_5 position-absolute">
          <Image src="/assets/img/3d-shape-2.png" alt="img" width={104} height={100}   />
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Analysis1;