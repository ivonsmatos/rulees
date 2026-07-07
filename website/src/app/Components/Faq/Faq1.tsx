"use client"
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

const Faq1 = () => {
        const faqContent = [
        {title:'O Rulees é só mais um app de resumo de reunião?', content:'Não. Resumir reunião é o começo. O Rulees entrega regras de negócio governadas: cada regra tem estado, versão, responsável e fonte, dentro do Rules Ledger. O foco é a rastreabilidade do requisito, não a ata.'},
        {title:'Como o Rulees evita que a IA invente requisitos?', content:'Toda regra criada pela IA aponta para a fala exata que a originou (source references) e nasce como rascunho. Uma pessoa precisa aprovar antes de a regra virar oficial — a IA nunca aprova sozinha.'},
        {title:'Meus dados e os do meu cliente ficam isolados e seguros?', content:'Sim. O Rulees é multi-tenant: cada organização tem seus dados isolados. As práticas seguem a LGPD, com trilha de auditoria e controle de acesso por papéis (RBAC).'},
        {title:'Consigo exportar as regras e documentos para outras ferramentas?', content:'Sim. Você gera documentação (resumo executivo, funcional, backlog) e exporta histórias e regras aprovadas para o Jira e o Confluence, mantendo o vínculo com a evidência original.'},
        {title:'Como começo a usar o Rulees?', content:'Crie uma conta gratuita, registre sua organização e seu primeiro projeto, e rode uma reunião. Em minutos você vê as primeiras regras candidatas surgindo — prontas para revisão humana.'},
      ];

      const accordionContentRef = useRef(null);
      const [openItemIndex, setOpenItemIndex] = useState(-1);
      const [firstItemOpen, setFirstItemOpen] = useState(true);
    
      const handleItemClick = index => {
        if (index === openItemIndex) {
          setOpenItemIndex(-1);
        } else {
          setOpenItemIndex(index);
        }
      };
      useEffect(() => {
        if (firstItemOpen) {
          setOpenItemIndex(0);
          setFirstItemOpen(false);
        }
      }, [firstItemOpen]);    

    return (
<section className="cs_faq cs_style_1 position-relative">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: faqContent.map((item) => ({
              '@type': 'Question',
              name: item.title,
              acceptedAnswer: { '@type': 'Answer', text: item.content },
            })),
          }),
        }}
      />
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="row cs_gap_y_30 position-relative z-1">
          <div className="col-lg-5">
            <div className="cs_section_heading cs_style_1 cs_faq_heading cs_mb_20">
              <div className="cs_section_subtitle cs_fs_18 cs_heading_color cs_mb_22">
                <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />  
                <span>Perguntas frequentes</span>
               <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
              </div>
              <h2 className="cs_section_title cs_fs_48 cs_semibold wow fadeInLeft">Tudo o que você precisa saber</h2>
              <p className="cs_card_desc cs_mb_32">As dúvidas mais comuns de quem está avaliando o Rulees para o time de produto ou para a sua software house.</p>
              <Link href="/faq" aria-label="Ver mais perguntas" className="cs_btn cs_style_1 cs_bg_1 cs_fs_14 cs_bold cs_white_color text-uppercase">
              <span>Ver mais perguntas</span>
              <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
              </Link>
            </div>
          </div>
          <div className="col-lg-7">
            <div className="cs_faq_wrapper_1">
            {faqContent.map((item, index) => (
              <div key={index} className={`cs_accordian cs_style_2 cs_gray_bg_2 cs_radius_10 position-relative ${index === openItemIndex ? "active" : "" }`} >
                <div onClick={() => handleItemClick(index)} className="cs_accordian_head">
                  <h3 className="cs_accordian_title cs_fs_20 cs_semibold mb-0">{item.title}</h3>
                  <span className="cs_accordian_toggler cs_center cs_radius_100 position-absolute">
                  <i className="bi bi-chevron-down"></i>
                  </span>
                </div>
                <div ref={accordionContentRef} className="cs_accordian_body">
                  <p>{item.content}</p>
                </div>
              </div>
              ))}

            </div>
          </div>
        </div>
        <div className="cs_faq_shape_3 position-absolute">
          <Image src="/assets/img/vector-12.svg" alt="img" width={109} height={112}   />  
        </div>
        <div className="cs_faq_shape_4 position-absolute">
          <Image src="/assets/img/vector-13.svg" alt="img" width={51} height={53}   />  
        </div>
        <div className="cs_faq_shape_5 position-absolute">
          <Image src="/assets/img/vector-14.svg" alt="img" width={108} height={123}   />  
        </div>
        <div className="cs_faq_shape_6 position-absolute">
          <Image src="/assets/img/vector-15.svg" alt="img" width={73} height={81}   />  
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Faq1;