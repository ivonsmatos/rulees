import BreadCumb from "../../Components/Common/BreadCumb";
import Toolset1 from "../../Components/Toolset/Toolset1";

export const metadata = {
  title: 'Integrações',
  description:
    'Conecte o Rulees às ferramentas que seu time já usa: exporte regras e documentos para o Jira e o Confluence, e integre com seu fluxo.',
  alternates: { canonical: '/integrations' },
};

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Integrações"
            ></BreadCumb>
            <Toolset1></Toolset1>
    </div>
  );
};

export default page;
