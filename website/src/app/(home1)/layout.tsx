import Footer2 from '../Components/Footer/Footer2';
import Header2 from '../Components/Header/Header2';

const layout = ({ children }) => {
    return (
        <div className='main-page-area'>
           <Header2></Header2>
            {children}
            <Footer2></Footer2>
        </div>
    );
};

export default layout;