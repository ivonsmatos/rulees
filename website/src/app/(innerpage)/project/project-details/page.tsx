import BreadCumb from '../../../Components/Common/BreadCumb';
import ProjectDetails from '../../../Components/ProjectDetails/ProjectDetails';

const page = () => {
  return (
    <div>
            <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Project Details"
            ></BreadCumb>         
            <ProjectDetails></ProjectDetails>       
    </div>
  );
};

export default page;