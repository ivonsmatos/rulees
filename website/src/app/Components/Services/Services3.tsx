import Link from 'next/link';
import ServiceCard1 from '../Card/ServiceCard1';
import Image from 'next/image';

const Services3 = () => {
           const bgImage = '/assets/img/feature-item-bg.svg';
    return (
 <section className="position-relative">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">

        <div className="cs_features_items_wrapper position-relative z-1">
          <div className="cs_feature_item cs_radius_20 cs_bg_filed" style={{ backgroundImage: `url(${bgImage})`}}>
            <h3 className="cs_fs_36 cs_semibold cs_white_color cs_mb_40">Tudo que sua reunião <br/> tem a dizer, organizado</h3>
            <Link href="/contact" aria-label="Começar agora" className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
            <span>Começar agora</span>
            <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
            </Link>
          </div>

          <ServiceCard1
            addclass="cs_bg_00"
            serviceicon="/assets/img/icons/code-icon.svg"
            title="Transcrição & extração de regras"
            featureList={[
                "Áudio normalizado pelo agente Scribe",
                "Regras candidatas pelo Observer",
                "Riscos e dependências detectados",
                "Evidência na fala original"
            ]}
            btnname="Saiba mais"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_1"
            serviceicon="/assets/img/icons/cloud-computing.svg"
            title="Rules Ledger & governança"
            featureList={[
                "Estado, versão e dono por regra",
                "Aprovação humana obrigatória",
                "A IA nunca aprova sozinha",
                "Histórico completo de decisões"
            ]}
            btnname="Saiba mais"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_2"
            serviceicon="/assets/img/icons/quality-assurance.svg"
            title="Detecção de conflitos (RAG)"
            featureList={[
                "Compara com o histórico do projeto",
                "Alerta de conflito e duplicidade",
                "Identifica regra desatualizada",
                "Isolamento por organização"
            ]}
            btnname="Saiba mais"
            btnurl="/service/service-details"
          ></ServiceCard1>

          <ServiceCard1
            addclass="cs_bg_3"
            serviceicon="/assets/img/icons/security.svg"
            title="Documentos & exportação"
            featureList={[
                "Resumo executivo e doc funcional",
                "Backlog e matriz de rastreabilidade",
                "Exportação em PDF e Markdown",
                "Envio para Jira e Confluence"
            ]}
            btnname="Saiba mais"
            btnurl="/service/service-details"
          ></ServiceCard1>

        </div>
      </div>
      <div className="cs_feature_shape_1 position-absolute">
        <Image src="/assets/img/3d-shape.png" alt="img" width={97} height={104}   />
      </div>
      <div className="cs_feature_shape_2 position-absolute">
        <Image src="/assets/img/spring-shape.png" alt="img" width={88} height={88}   />
      </div>
    </section>
    );
};

export default Services3;
