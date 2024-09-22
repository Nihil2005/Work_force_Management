import React from 'react';

const Homepage = () => {
  return (
    <div className='bg-black  h-screen flex flex-col items-center justify-center'>
      

      <video
        className='h-[650px] mt-8 w-[750px]'
        src='/Abstract Creative Idea Brain Bulb Logo.mp4'
        autoPlay
        loop
        muted
        controls
      />
    </div>
  );
};

export default Homepage;
