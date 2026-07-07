const Counter1 = () => {
    const bgImage = '/assets/img/counter-bg-2.svg';
    return (
    <div className="cs_counter cs_style_1 cs_type_1 cs_accent_bg" style={{ backgroundImage: `url(${bgImage})`}} >
      <div className="container">
        <div className="row cs_gap_y_30">
          <div className="col-lg-3 col-sm-6">
            <div className="cs_numberbox cs_center_column text-center">
              <div className="cs_counter_number cs_fs_48 cs_semibold cs_white_color cs_mb_10">5</div>
              <p className="cs_fs_24 cs_white_color mb-0">Agentes de IA <br/> especializados</p>
            </div>
          </div>
          <div className="col-lg-3 col-sm-6">
            <div className="cs_numberbox cs_center_column text-center">
              <div className="cs_counter_number cs_fs_48 cs_semibold cs_white_color cs_mb_10">100%</div>
              <p className="cs_fs_24 cs_white_color mb-0">Regras com <br/> fonte rastreável</p>
            </div>
          </div>
          <div className="col-lg-3 col-sm-6">
            <div className="cs_numberbox cs_center_column text-center">
              <div className="cs_counter_number cs_fs_48 cs_semibold cs_white_color cs_mb_10">10</div>
              <p className="cs_fs_24 cs_white_color mb-0">Estados no <br/> Rules Ledger</p>
            </div>
          </div>
          <div className="col-lg-3 col-sm-6">
            <div className="cs_numberbox cs_center_column text-center">
              <div className="cs_counter_number cs_fs_48 cs_semibold cs_white_color cs_mb_10">6</div>
              <p className="cs_fs_24 cs_white_color mb-0">Tipos de <br/> documento gerados</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    );
};

export default Counter1;