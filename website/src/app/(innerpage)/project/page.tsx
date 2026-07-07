import BreadCumb from "../../Components/Common/BreadCumb";
import Project1 from "../../Components/Project/Project1";

export const metadata = {
  title: 'Casos de uso',
  description:
    'Como software houses, consultorias e times de produto usam o Rulees para transformar reuniões em requisitos rastreáveis.',
  alternates: { canonical: '/project' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Casos de uso"
            ></BreadCumb>
            <Project1></Project1>
    </div>
  );
};

export default page;
