import Image from "next/image";
import Link from "next/link";

const Feature4 = () => {
    return (
 <section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_card cs_style_2 position-relative z-1">
          <div className="row cs_gap_y_40">
            <div className="col-lg-6 order-lg-2">
              <div className="cs_card_thumbnail">
                <Image src="/assets/img/dashboard-2.png" alt="img" width={924} height={666}   />  
              </div>
            </div>
            <div className="col-lg-6 order-lg-1">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_34">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />   
                    <span>Como funciona</span>
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInUp">Da reunião à regra aprovada, em um só fluxo</h2>
                  <p className="mb-0">Você conduz a reunião normalmente. O Rulees escuta, transcreve e a IA já começa a separar o que é regra, decisão, dúvida e risco — tudo com a fonte na fala original.</p>
                </div>
                <div className="cs_service_item cs_radius_15 cs_gray_bg_2 cs_mb_24 cs_active">
                  <h3 className="cs_service_title cs_fs_24 cs_semibold cs_mb_8">1. A IA escuta e organiza</h3>
                  <p className="mb-0">Os agentes Scribe e Observer transformam a conversa em regras candidatas, com evidência. Em tempo real, durante a própria reunião.</p>
                </div>
                <div className="cs_service_item cs_radius_15 cs_mb_48">
                  <h3 className="cs_service_title cs_fs_24 cs_semibold cs_mb_8">2. Pessoas aprovam</h3>
                  <p className="mb-0">Sua equipe revisa cada regra no Rules Ledger e aprova o que é oficial. A IA sugere; quem decide é o time — sem achismo.</p>
                </div>
                <div className="cs_btns_group">
                  <Link href="/contact" aria-label="Começar grátis" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
                  <span>Começar grátis</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                  </Link>
                  <div className="cs_client_info_wrapper">
                    <div>
                      <h3 className="cs_fs_30 cs_semibold mb-0">100%</h3>
                      <p className="cs_heading_color mb-0">Regras com fonte</p>
                    </div>
                  </div>
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

export default Feature4;