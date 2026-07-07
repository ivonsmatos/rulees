import BreadCumb from "../../Components/Common/BreadCumb";
import Faq1 from "../../Components/Faq/Faq1";

export const metadata = {
  title: 'Perguntas frequentes',
  description:
    'Anti-alucinação, LGPD, integrações e como começar: as dúvidas mais comuns de quem está avaliando o Rulees.',
  alternates: { canonical: '/faq' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Perguntas frequentes"
            ></BreadCumb>
            <Faq1></Faq1>
    </div>
  );
};

export default page;
