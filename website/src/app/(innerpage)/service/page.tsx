import BreadCumb from '../../Components/Common/BreadCumb';
import Services3 from '../../Components/Services/Services3';
import Feature5 from '../../Components/Feature/Feature5';
import Analysis1 from '../../Components/Analysis/Analysis1';

export const metadata = {
  title: 'Recursos',
  description:
    'Transcrição inteligente, extração de regras, detecção de conflitos, Rules Ledger e documentação rastreável. Conheça os recursos do Rulees.',
  alternates: { canonical: '/service' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Recursos do Rulees"
            ></BreadCumb>
             <Services3></Services3>
             <Feature5></Feature5>
             <Analysis1></Analysis1>
    </div>
  );
};

export default page;
