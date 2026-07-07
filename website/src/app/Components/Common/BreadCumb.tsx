import Link from "next/link";

const BreadCumb = ({Title,bgimg}) => {
    
    return (

    <section className="cs_page_heading cs_bg_filed text-center cs_gray_bg_2 position-relative overflow-hidden" style={{ backgroundImage: `url(${bgimg})`}} >
      <div className="container">
        <h1 className="cs_fs_64 cs_bold cs_mb_8">{Title}</h1>
        <ol className="breadcrumb cs_fs_18 cs_heading_font">
          <li className="breadcrumb-item"><Link aria-label="Voltar para a página inicial" href="/">Início</Link></li>
          <li className="breadcrumb-item active">{Title}</li>
        </ol>
      </div>
    </section>


    );
};

export default BreadCumb;