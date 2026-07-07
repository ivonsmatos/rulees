import Image from "next/image";

const Feature2 = () => {
    return (
 <section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_card cs_style_1 cs_type_2 position-relative z-1">
          <div className="row cs_gap_y_50 position-relative z-1">
            <div className="col-lg-7">
              <div className="cs_card_thumbnail position-relative">
                <Image className="cs_radius_30" src="/assets/img/rulees/feature-collab.jpg" alt="Equipe revisando requisitos e regras de negócio geradas pelo Rulees" width={746} height={560}   />
              </div>
            </div>
            <div className="col-lg-5">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_33">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
                    <span>Por que o Rulees</span>
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInUp">Feito para times que não podem errar requisito</h2>
                  <p className="cs_card_desc mb-0">Segurança, evidência e tempo real em um só lugar. O Rulees foi desenhado para reuniões de negócio de verdade — não para virar mais uma ata esquecida.</p>
                </div>
                <div className="cs_iconbox_wrapper_3">
                  <div className="cs_iconbox cs_style_5">
                    <span className="cs_iconbox_icon cs_center cs_radius_100 cs_mb_18">
                      <Image src="/assets/img/icons/safety.svg" alt="img" width={37} height={37}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_18 cs_semibold cs_mb_4">Seguro e em conformidade</h3>
                      <p className="mb-0">Isolamento por organização e práticas alinhadas à LGPD.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_5">
                    <span className="cs_iconbox_icon cs_bg_1 cs_center cs_radius_100 cs_mb_18">
                      <Image src="/assets/img/icons/analytics-2.svg" alt="img" width={45} height={36}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_18 cs_semibold cs_mb_4">Evidência rastreável</h3>
                      <p className="mb-0">Cada regra ligada à fala original, sem alucinação.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_5">
                    <span className="cs_iconbox_icon cs_bg_2 cs_center cs_radius_100 cs_mb_18">
                      <Image src="/assets/img/icons/automation.svg" alt="img" width={36} height={36}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_18 cs_semibold cs_mb_4">Análise em tempo real</h3>
                      <p className="mb-0">Regras e dúvidas aparecem durante a própria reunião.</p>
                    </div>
                  </div>
                  <div className="cs_iconbox cs_style_5">
                    <span className="cs_iconbox_icon cs_bg_3 cs_center cs_radius_100 cs_mb_18">
                      <Image src="/assets/img/icons/easy-intinsive.svg" alt="img" width={37} height={36}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <h3 className="cs_fs_18 cs_semibold cs_mb_4">Simples de adotar</h3>
                      <p className="mb-0">Do áudio ao documento sem fricção para o time.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_vector_shape_8 position-absolute">
          <Image src="/assets/img/vector-11.svg" alt="img" width={79} height={79}   /> 
        </div>
        <div className="cs_vector_shape_9 position-absolute"></div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="cs_height_90 cs_height_lg_90"></div>
    </section>
    );
};

export default Feature2;