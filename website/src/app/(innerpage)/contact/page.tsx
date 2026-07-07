import BreadCumb from '../../Components/Common/BreadCumb';
import Contact from '../../Components/Contact/Contact';

export const metadata = {
  title: 'Fale com a gente',
  description:
    'Quer ver o Rulees transformando suas reuniões em regras de negócio rastreáveis? Fale com o nosso time e comece grátis.',
  alternates: { canonical: '/contact' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Fale com a gente"
            ></BreadCumb>
            <Contact></Contact>
    </div>
  );
};

export default page;
