const Counter2 = () => {
  const bgImage = '/assets/img/counter-bg-1.svg';
    return (
  <div className="cs_counter cs_style_1">
      <div className="cs_counter_content_wrapper cs_accent_bg cs_radius_30 cs_bg_filed" style={{ backgroundImage: `url(${bgImage})`}} >
        <div className="container">
          <div className="row cs_gap_y_30">
            <div className="col-lg-3 col-sm-6">
              <div className="cs_numberbox">
                <div className="cs_counter_number cs_fs_74 cs_semibold cs_white_color cs_mb_10">
                  <span className="odometer" data-count-to="56">56</span>K+
                </div>
                <p className="cs_fs_18 cs_white_color mb-0">Customers visit app <br/> every months</p>
              </div>
            </div>
            <div className="col-lg-3 col-sm-6">
              <div className="cs_numberbox">
                <div className="cs_counter_number cs_fs_74 cs_semibold cs_white_color cs_mb_10">
                  <span className="odometer" data-count-to="32">32</span>K+
                </div>
                <p className="cs_fs_18 cs_white_color mb-0">Total downloaded of <br/> our app</p>
              </div>
            </div>
            <div className="col-lg-3 col-sm-6">
              <div className="cs_numberbox">
                <div className="cs_counter_number cs_fs_74 cs_semibold cs_white_color cs_mb_10">
                  <span className="odometer" data-count-to="156">156</span>K+
                </div>
                <p className="cs_fs_18 cs_white_color mb-0">Total Members of Relatix <br/> App Users</p>
              </div>
            </div>
            <div className="col-lg-3 col-sm-6">
              <div className="cs_numberbox">
                <div className="cs_counter_number cs_fs_74 cs_semibold cs_white_color cs_mb_10">
                  <span className="odometer" data-count-to="42">42</span>+
                </div>
                <p className="cs_fs_18 cs_white_color mb-0">Satisfaction rate from our <br/> customers.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    );
};

export default Counter2;