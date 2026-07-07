import BlogDetails from "../../../Components/BlogDetails/BlogDetails";
import BreadCumb from "../../../Components/Common/BreadCumb";

const page = () => {
  return (
    <div>
             <BreadCumb
                bgimg="/assets/img/page-heading-bg.svg"
                Title="Blog Details"
            ></BreadCumb>      
            <BlogDetails></BlogDetails>          
    </div>
  );
};

export default page;