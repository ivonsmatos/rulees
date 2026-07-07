import BreadCumb from '../../../Components/Common/BreadCumb';
import ServiceDetails from '../../../Components/SerciceDetails/ServiceDetails';

const page = () => {
  return (
    <div>
             <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Service Details"
            ></BreadCumb>
            <ServiceDetails></ServiceDetails>      
    </div>
  );
};

export default page;