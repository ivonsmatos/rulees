import BreadCumb from '../../Components/Common/BreadCumb';
import Feature4 from '../../Components/Feature/Feature4';
import Review1 from '../../Components/Review/Review1';
import Analysis1 from '../../Components/Analysis/Analysis1';
import Counter1 from '../../Components/Counter/Counter1';
import Story1 from '../../Components/Story/Story1';

export const metadata = {
  title: 'Como funciona',
  description:
    'Da reunião ao requisito aprovado: entenda como o Rulees usa IA e controle humano para transformar conversas em regras de negócio rastreáveis.',
  alternates: { canonical: '/about' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Como funciona"
            ></BreadCumb>
            <Feature4></Feature4>
            <Review1></Review1>
            <Analysis1></Analysis1>
            <Counter1></Counter1>
            <Story1></Story1>
    </div>
  );
};

export default page;
