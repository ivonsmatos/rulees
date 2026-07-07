import Image from "next/image";

const Contact = () => {
    const bgImage = '/assets/img/contact-img-1.jpg';
    return (
        <div>
    <section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="row cs_gap_y_30 align-items-center">
          <div className="col-lg-6">
            <div className="cs_contact_desc">
              <ul className="cs_contact_info_list cs_mp_0">
                <li>
                  <div className="cs_iconbox cs_style_6">
                    <span className="cs_iconbox_icon cs_center cs_radius_100 position-relative">
                      <Image src="/assets/img/icons/call.svg" alt="img" width={30} height={30}   />  
                    </span>
                    <div className="cs_iconbox_info">
                      <p className="cs_white_color cs_heading_font cs_mb_4">Suporte</p>
                      <a href="mailto:suporte@rulees.com.br" aria-label="Enviar e-mail para o suporte" className="cs_fs_24 cs_bold cs_white_color cs_heading_font">suporte@rulees.com.br</a>
                    </div>
                  </div>
                </li>
                <li>
                  <div className="cs_iconbox cs_style_6">
                    <span className="cs_iconbox_icon cs_center cs_radius_100 position-relative">
                      <Image src="/assets/img/icons/email.svg" alt="img" width={30} height={30}   />  
                    </span>
                    <div className="cs_iconbox_info">
                      <p className="cs_white_color cs_heading_font cs_mb_4">Comercial</p>
                      <a href="mailto:contato@rulees.com.br" aria-label="Enviar e-mail comercial" className="cs_fs_24 cs_bold cs_white_color cs_heading_font">contato@rulees.com.br</a>
                    </div>
                  </div>
                </li>
                <li>
                  <div className="cs_iconbox cs_style_6">
                    <span className="cs_iconbox_icon cs_center cs_radius_100 position-relative">
                      <Image src="/assets/img/icons/call.svg" alt="img" width={30} height={30}   />
                    </span>
                    <div className="cs_iconbox_info">
                      <p className="cs_white_color cs_heading_font cs_mb_4">WhatsApp</p>
                      <a href="https://wa.me/5511941906079" target="_blank" rel="noopener" aria-label="Falar no WhatsApp" className="cs_fs_24 cs_bold cs_white_color cs_heading_font">(11) 94190-6079</a>
                    </div>
                  </div>
                </li>
              </ul>
              <a  aria-label="Click to play video" className="cs_video cs_style_1 cs_center cs_video_open cs_bg_filed position-relative"  style={{ backgroundImage: `url(${bgImage})`}} >
              </a>
            </div>
          </div>
          <div className="col-lg-6">
            <div className="cs_contact_form_wrapper">
              <h2 className="cs_fs_36 cs_semibold cs_mb_21">Pronto para começar?</h2>
              <p className="cs_mb_26">Conte sobre o seu time e o seu desafio com requisitos. A gente responde rápido e te mostra o Rulees transformando reuniões em regras rastreáveis.</p>
              <form action="https://api.web3forms.com/submit" method="POST" className="cs_contact_form row cs_gap_y_20" id="cs_form">
                <input type="hidden" name="access_key" value="YOUR_ACCESS_KEY_HERE" />
                <div className="col-sm-6">
                  <label htmlFor="name">Seu nome*</label>
                  <input type="text" name="name" id="name" placeholder="Seu nome" className="cs_form_field cs_radius_8" />
                </div>
                <div className="col-sm-6">
                  <label htmlFor="email">Seu e-mail*</label>
                  <input type="email" name="email" id="email" placeholder="E-mail" className="cs_form_field cs_radius_8" />
                </div>
                <div className="col-sm-12">
                  <label htmlFor="message">Mensagem*</label>
                  <textarea name="comment" rows={6} id="message" placeholder="Escreva sua mensagem" className="cs_form_field cs_radius_8"></textarea>
                </div>
                <div className="col-md-12">
                  <button type="submit" aria-label="Enviar mensagem" className="cs_btn cs_style_1 cs_bg_1 cs_semibold cs_white_color text-capitalize">
                  <span>Enviar mensagem</span>
                  <span className="cs_btn_icon"><i className="bi bi-arrow-right"></i></span>
                  </button>
                  <div id="cs_result" className="cs_result"></div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
        </div>
    );
};

export default Contact;