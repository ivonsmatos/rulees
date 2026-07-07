import Image from "next/image";
import Link from "next/link";

const Services2 = () => {

        const teamContent = [
        {img:'/assets/img/services-icon1.svg', title:'Transcrição inteligente', content:'O agente Scribe normaliza o áudio da reunião em texto limpo, preservando exatamente o que foi dito — sem inventar nada.'},
        {img:'/assets/img/services-icon2.svg', title:'Extração de regras', content:'O agente Observer identifica regras de negócio, riscos e dependências na conversa e transforma em regras candidatas com fonte.'},
        {img:'/assets/img/services-icon3.svg', title:'Detecção de conflitos', content:'O RAG Guardian compara cada nova regra com o histórico do projeto e alerta sobre conflito, duplicidade ou regra desatualizada.'},
        {img:'/assets/img/services-icon4.svg', title:'Perguntas inteligentes', content:'O agente Inquisitor encontra lacunas e gera as perguntas certas para fechar requisitos ambíguos antes de virar bug.'},
        {img:'/assets/img/services-icon5.svg', title:'Rules Ledger', content:'Cada regra tem estado, versão, fonte e dono. A IA sugere; uma pessoa aprova. Governança de requisitos de ponta a ponta.'},
        {img:'/assets/img/services-icon6.svg', title:'Documentos e exportação', content:'Gere resumo executivo, documento funcional e backlog rastreável — e exporte para o Jira e o Confluence em um clique.'},
      ];


    return (
<section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_center_column cs_mb_47 text-center position-relative z-1">
          <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />   
            <span>O que a IA faz por você</span>
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
          </div>
          <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInUp">Cinco agentes de IA, um objetivo: clareza</h2>
          <p className="mb-0">Da fala na reunião ao requisito aprovado. O Rulees combina agentes especializados <br/> para que nada importante se perca — e tudo continue rastreável.</p>
        </div>
        <div className="row cs_row_gap_30 cs_gap_y_30 position-relative z-2">

        {teamContent.map((item, i) => (
          <div key={i} className="col-xl-4 col-md-6">
            <div className="cs_iconbox cs_style_4 cs_radius_15 position-relative overflow-hidden">
              <div className="cs_iconbox_content cs_radius_15 position-relative">
                <div className="cs_iconbox_header cs_mb_17">
                  <span className="cs_iconbox_icon cs_heading_color">
                    <Image src={item.img} alt="img" width={60} height={60}   />  
                  </span>
                  <h3 className="cs_iconbox_title cs_fs_24 cs_semibold mb-0"><Link href="/service/service-details" aria-label="Service details page link">{item.title}</Link></h3>
                </div>
                <div className="cs_iconbox_info">
                  <p className="cs_mb_25">{item.content}</p>
                  <Link href="/service/service-details" aria-label="Service details page link" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_heading_color text-uppercase">
                  <span>Saiba mais</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                  </Link>
                </div>
              </div>
              <div className="cs_service_shape position-absolute">
                <Image src="/assets/img/service-shape-2.svg" alt="img" width={323} height={218}   />   
              </div>
            </div>
          </div>
           ))}
         


        </div>
        <div className="cs_service_shape_1 position-absolute start-0 bottom-0">
          <Image src="/assets/img/service-shape-1.svg" alt="img" width={1905} height={1445}   /> 
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Services2;