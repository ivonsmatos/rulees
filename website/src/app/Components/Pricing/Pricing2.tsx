"use client"
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';

const Pricing2 = () => {

  const [billingType, setBillingType] = useState('yearly');
  const isMonthly = billingType === 'monthly';
  const pricingData = [
    {
      title: 'Free',
      monthly: '0',
      yearly: '0',
      features: [
        'Até 3 usuários',
        '5 reuniões por mês',
        'Transcrição e extração de regras',
        'Rules Ledger com aprovação humana',
        'Exportação em PDF',
      ],
    },
    {
      title: 'Pro',
      badge: 'Mais popular',
      monthly: '149',
      yearly: '119',
      features: [
        'Até 10 usuários',
        'Reuniões ilimitadas',
        'RAG: detecção de conflitos e duplicidade',
        'Perguntas inteligentes e decisões',
        'Exportação para Jira e Confluence',
      ],
    },
    {
      title: 'Business',
      monthly: '349',
      yearly: '279',
      features: [
        'Usuários ilimitados',
        'Multi-projeto e papéis avançados (RBAC)',
        'Trilha de auditoria e LGPD',
        'Modelos de documento personalizados',
        'Suporte prioritário',
      ],
    },
  ];

    return (

    <section
      className="position-relative cs_bg_filed cs_radius_50_50 cs_mt_90 position-relative z-1"
      style={{ backgroundImage: `url("/assets/img/pricing-bg-1.svg")` }}
    >
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_style_1 cs_center_column cs_mb_60 text-center position-relative z-1">
          <div className="cs_section_subtitle cs_type_1 cs_fs_18 cs_white_color cs_mb_22">
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   /> 
            <span>Planos</span>
            <Image src="/assets/img/icons/star-1.svg" alt="img" width={15} height={15}   />
          </div>
          <h2 className="cs_section_title cs_fs_48 cs_semibold cs_white_color wow fadeInDown">
            Comece grátis, cresça quando precisar
          </h2>
          <p className="cs_white_color cs_mb_33">
            Sem cartão de crédito para começar. Você só evolui de plano quando o Rulees <br />
            já estiver economizando horas de retrabalho do seu time.
          </p>
          <div className="cs_center">
            <ul className="cs_pricing_control cs_type_1 cs_center cs_mp_0 cs_fs_14 cs_white_color cs_bold text-uppercase position-relative">
              <li className={billingType === 'yearly' ? 'active' : ''} onClick={() => setBillingType('yearly')}>
                <a href="yearly" aria-label="Cobrança anual" onClick={(e) => e.preventDefault()}>
                  Anual
                </a>
                <div className="cs_offer_info cs_theme_color_4 cs_heading_font cs_normal position-absolute">
                  <span>Economize 20%</span>
                </div>
              </li>
              <li className={billingType === 'monthly' ? 'active' : ''} onClick={() => setBillingType('monthly')}>
                <a href="monthly" aria-label="Cobrança mensal" onClick={(e) => e.preventDefault()}>
                  Mensal
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="row cs_row_gap_30 cs_gap_y_30">
          {pricingData.map((plan, index) => (
            <div className="col-lg-4" key={index}>
              <div className="cs_pricing_table cs_style_1 cs_type_1 cs_radius_20 position-relative">
                {plan.badge && (
                  <div className="cs_pricing_badge cs_theme_bg_4 cs_medium cs_heading_color text-center position-absolute">
                    {plan.badge}
                  </div>
                )}
                <div className="cs_pricing_table_heading cs_mb_18">
                  <h2 className="cs_plan_title cs_fs_24 cs_semibold cs_white_color mb-0">{plan.title}</h2>
                </div>
                <div className="cs_pricing_info cs_mb_20">
                  <div className="cs_price cs_fs_74 cs_semibold cs_white_color cs_heading_font cs_mb_4">
                    R${isMonthly ? plan.monthly : plan.yearly}
                    <small>por mês</small>
                  </div>
                  <p className="cs_white_color mb-0">
                    Tudo o que seu time precisa para transformar reuniões em requisitos rastreáveis.
                  </p>
                </div>
                <div className="cs_separator cs_mb_22"></div>
                <div className="cs_feature_wrapper cs_mb_30">
                  <h3 className="cs_fs_18 cs_semibold cs_white_color cs_mb_15">O que está incluso</h3>
                  <ul className="cs_pricing_feature_list cs_mp_0">
                    {plan.features.map((feature, i) => (
                      <li key={i}>
                        <span className="cs_feature_icon">
                          
                          <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                              d="M12.2442 0.289465L5.02298 7.10457L2.68046 4.6782C1.1639 3.21126 -0.947636 5.40321 0.466273 6.97165L3.86805 10.4952C3.89139 10.5194 3.93805 10.5701 3.96372 10.5919C4.57501 11.1719 5.52228 11.1284 6.08225 10.4952L13.7211 1.81682C14.5914 0.787306 13.2358 -0.611965 12.2465 0.289465H12.2442Z"
                              fill="currentColor"
                            />
                          </svg>
                        </span>
                        <span className="cs_feature_title">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <Link
                  href="/contact"
                  aria-label="Assinar plano"
                  className="cs_btn cs_style_1 cs_fs_14 cs_bold cs_heading_color w-100 text-uppercase"
                >
                  <span>Começar</span>
                  <span className="cs_btn_icon">
                    <i className="fa-solid fa-arrow-right"></i>
                  </span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>

    );
};

export default Pricing2;