import BreadCumb from "../../Components/Common/BreadCumb";
import Pricing4 from "../../Components/Pricing/Pricing4";

export const metadata = {
  title: 'Planos e preços',
  description:
    'Comece grátis e evolua quando o Rulees já estiver economizando horas de retrabalho. Planos para times de produto e software houses.',
  alternates: { canonical: '/pricing' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Planos e preços"
            ></BreadCumb>
            <Pricing4></Pricing4>
    </div>
  );
};

export default page;
