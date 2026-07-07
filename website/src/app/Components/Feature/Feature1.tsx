import Image from "next/image";
import Link from "next/link";

const Feature1 = () => {
    return (
 <section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_card cs_style_2 position-relative z-1">
          <div className="row cs_gap_y_40">
            <div className="col-lg-6 order-lg-2">
              <div className="cs_card_thumbnail">
                <Image src="/assets/img/dashboard-2.png" alt="Painel do Rulees mostrando o Rules Ledger com regras, estados e fonte" width={924} height={666}   />
              </div>
            </div>
            <div className="col-lg-6 order-lg-1">
              <div className="cs_card_content">
                <div className="cs_section_heading cs_style_1 cs_mb_34">
                  <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />   
                    <span>Rules Ledger</span>
                    <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
                  </div>
                  <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInUp">Do rascunho à regra oficial, com controle humano</h2>
                  <p className="mb-0">O Rules Ledger é o livro-razão das suas regras de negócio: cada uma tem histórico, versão e responsável. A IA propõe; a sua equipe decide.</p>
                </div>
                <div className="cs_service_item cs_radius_15 cs_gray_bg_2 cs_mb_24 cs_active">
                  <h3 className="cs_service_title cs_fs_24 cs_semibold cs_mb_8">Aprovação humana</h3>
                  <p className="mb-0">Nenhuma regra vira oficial sem revisão. A IA nunca aprova sozinha — você mantém o controle do que entra na documentação e no backlog.</p>
                </div>
                <div className="cs_service_item cs_radius_15 cs_mb_48">
                  <h3 className="cs_service_title cs_fs_24 cs_semibold cs_mb_8">Rastreabilidade total</h3>
                  <p className="mb-0">Toda regra aponta para a fala exata que a originou. Acabou o “quem decidiu isso?”: a evidência fica registrada e auditável para sempre.</p>
                </div>
                <div className="cs_btns_group">
                  <Link href="/contact" aria-label="Começar grátis" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
                  <span>Começar grátis</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                  </Link>
                  <div className="cs_client_info_wrapper">
                    <Image src="/assets/img/customers-group.png" alt="img" width={151} height={58}   />
                    <div>
                      <h3 className="cs_fs_30 cs_semibold mb-0">100% <span></span></h3>
                      <p className="cs_heading_color mb-0">Regras com fonte</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="cs_vector_shape_6 position-absolute"></div>
        <div className="cs_vector_shape_7 position-absolute"></div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>

    );
};

export default Feature1;