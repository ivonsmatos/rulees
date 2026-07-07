import Image from "next/image";

const ServiceDetails = () => {
    return (
 <section>
      <div className="cs_height_120 cs_height_lg_80"></div>
      <div className="container">
        <div className="cs_service_details">
          <div className="cs_banner cs_radius_50">
            <Image src="/assets/img/service_img-1.jpg" alt="img" width={1296} height={621}   />
          </div>
          <p>Our UI/UX design services are crafted to elevate your digital presence with precision and creativity. We begin by understanding your goals and your audience, ensuring that every design decision aligns with your brand’s vision. Our approach integrates user research, wireframing, and prototyping to create intuitive and engaging interfaces.
          </p>
          <p>We focus on delivering seamless user experiences that drive engagement and satisfaction. From concept to launch, our team is dedicated to design solutions that are not only visually appealing but also functionally robust. We continuously test and refine our designs to meet the highest standards of usability.</p>
          <h2>Boost your brand with the help of our creative agencys UX design.</h2>
          <p>Enhance your brand’s impact with our creative agencys expert UX design services. We will craft engaging and intuitive user experiences that elevate your brand and captivate your audience.</p>
          <ul>
            <li>consectetur placerat augue vestibulum</li>
            <li> adipiscing elit Etiam aliquam, enim vitae</li>
            <li>Mauris tincidunt a eget facilisis  Quisque</li>
            <li>Donec at augue ante Nam posuere mauris</li>
            <li>Lorem ipsum dolor sit amet, consectetur</li>
            <li>quis pretium elit placerat id Fusce egestas</li>
          </ul>
          <div className="row cs_row_gap_30 cs_gap_y_30 cs_mb_32">
            <div className="col-md-6">
              <div className="cs_radius_20">
                <Image src="/assets/img/service_img-2.jpg" alt="img" width={633} height={334}   />
              </div>
            </div>
            <div className="col-md-6">
              <div className="cs_radius_20">
                <Image src="/assets/img/service_img-3.jpg" alt="img" width={633} height={334}   />
              </div>
            </div>
          </div>
          <p>Nam posuere mauris enim, quis pretium elit placerat id  Fusce egestas nisi vel ipsum vehicula facilisis In pulvinar imperdiet venenatis  className aptent taciti sociosqu ad litora torent per conubia nostra, per inceptos himenaeos. Donec eu pulvinar lorem. Etiam vestibulum ligula quis nisl feugiat, consectetur placerat augue vestibulum  Nulla aliquam elit eu diam pharetra.Nam posuere mauris enim, </p>
          <p>Nam posuere mauris enim, quis pretium elit placerat id  Fusce egestas nisi vel ipsum vehicula facilisis In pulvinar imperdiet venenatis  className aptent taciti sociosqu ad litora torent per conubia nostra, per inceptos himenaeos. Donec eu pulvinar lorem. </p>
        </div>
      </div>
      <div className="cs_height_120 cs_height_lg_80"></div>
    </section>
    );
};

export default ServiceDetails;