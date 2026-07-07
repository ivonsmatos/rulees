import Image from 'next/image';
import Link from 'next/link';
import React from 'react';

const ServiceCard1 = React.memo(({addclass, serviceicon, title, featureList, btnname, btnurl} : any ) => {
    return (
          <div className="cs_feature_item cs_white_bg cs_radius_20">
            <span className={`cs_feature_icon cs_center cs_radius_12 cs_mb_15 ${addclass}`}>
              <Image src={serviceicon} alt="img" width={30} height={30}   />
            </span>
            <h3 className="cs_fs_24 cs_semibold cs_mb_6">
              <Link href={btnurl} aria-label="Service details link">{title}</Link>
            </h3>
            <ul className="cs_features_list cs_mp_0">
            {featureList?.map((item, index) => (
              <li key={index}>
                <Image src="/assets/img/icons/caret-icon.svg" alt="img" width={8} height={11}   />
                <span>{item}</span>
              </li>
            ))}
            </ul>
            <Link href={btnurl} aria-label="Service details link" className="cs_text_btn cs_fs_14 cs_bold text-uppercase">
            <span>{btnname}</span>
            <span className="cs_btn_icon"><i className="bi bi-arrow-right" /></span>
            </Link>
          </div>
    );
});

ServiceCard1.displayName = 'ServiceCard1';

export default ServiceCard1;