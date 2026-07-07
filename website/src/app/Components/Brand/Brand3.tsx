
const Brand3 = () => {

        const chooseContent = [
        {img:'/assets/img/brand-1.svg'},                         
        {img:'/assets/img/brand-2.svg'},                         
        {img:'/assets/img/brand-3.svg'},                         
        {img:'/assets/img/brand-4.svg'},                         
        {img:'/assets/img/brand-5.svg'},                         
        {img:'/assets/img/brand-6.svg'},                         
      ]; 

    return (
<section className="cs_brands_slider">
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_section_heading cs_center cs_mb_25">
          <h3 className="cs_brand_title cs_fs_20 text-capitalize mb-0">Millions of clients trust us.</h3>
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
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default Brand3;