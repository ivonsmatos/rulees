import BreadCumb from '../../Components/Common/BreadCumb';
import Blog4 from '../../Components/Blog/Blog4';

const page = () => {
  return (
    <div>
             <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Blog Standard"
            ></BreadCumb>     
            <Blog4></Blog4>       
    </div>
  );
};

export default page;