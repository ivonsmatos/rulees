import Header4 from '../Components/Header/Header4';
import Footer2 from '../Components/Footer/Footer2';

const DefalultLayout = ({ children }) => {
    return (
        <div className='main-page-area'>
            <Header4></Header4>
            {children}
            <Footer2></Footer2>
        </div>
    );
};

export default DefalultLayout;