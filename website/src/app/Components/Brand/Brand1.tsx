
const Brand1 = () => {

    const chooseContent = [
        {img:'/assets/img/brand-6.svg'},                         
        {img:'/assets/img/brand-7.svg'},                         
        {img:'/assets/img/brand-8.svg'},                         
        {img:'/assets/img/brand-9.svg'},                         
        {img:'/assets/img/brand-10.svg'},                         
        {img:'/assets/img/brand-1.svg'},                         
      ]; 

    return (
 <section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_mb_31">
          <h2 className="cs_fs_20 cs_normal mb-0">Trusted by 100,000+ teams globally at innovative companies</h2>
        </div>
        <div className="cs_horizontal_slider_wrapper">
          <div className="cs_slider_in">
            <div className="cs_brands_list">
            {chooseContent.map((item, i) => (
              <div key={i} className="cs_center">
                <img src={item.img} alt="brand-img" />
              </div>
                ))}
            </div>
            <div className="cs_brands_list">
            {chooseContent.map((item, i) => (
              <div key={i} className="cs_center">
               <img src={item.img} alt="brand-img" />
              </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </section>
    );
};

export default Brand1;