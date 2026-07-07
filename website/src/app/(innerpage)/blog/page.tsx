import BreadCumb from '../../Components/Common/BreadCumb';
import Blog5 from '../../Components/Blog/Blog5';

export const metadata = {
  title: 'Blog',
  description:
    'Ideias sobre requisitos, produto e IA sem alucinação — conteúdo para quem leva engenharia de requisitos a sério.',
  alternates: { canonical: '/blog' },
};

const page = () => {
  return (
    <div>
              <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Blog"
            ></BreadCumb>
            <Blog5></Blog5>
    </div>
  );
};

export default page;
