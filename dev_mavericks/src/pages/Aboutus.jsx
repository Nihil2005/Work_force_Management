'use client';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { FaInstagram } from 'react-icons/fa';

const membersData = [
  { name: "Nihil", role: "Founder & CEO", description: "Nihil is the visionary behind the project, overseeing all strategic aspects.", instagram: "https://www.instagram.com/nihil_feliz" },
  { name: "Syed", role: "Developer", description: "Syed handles the technical implementation and development of the token.", },
  { name: "Aromal", role: "Designer", description: "Aromal is responsible for the user experience and design of our interfaces." },
  { name: "Rahith", role: "Marketing", description: "Rahith manages our marketing strategies and community engagement.", },
  { name: "Dinesh", role: "Marketing", description: "Dinesh manages our marketing strategies and community engagement." }
];

const Aboutus = () => {
  const membersRef = useRef(null);

  useEffect(() => {
    gsap.fromTo(membersRef.current.querySelectorAll('.member-card'),
      { opacity: 0, y: 100, scale: 0.9 },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        stagger: 0.3,
        duration: 1.2,
        ease: "power4.out",
      }
    );
  }, []);

  return (
    <div className="bg-gray-900 p-9 text-white min-h-screen py-10">
      <h1 className="text-5xl font-bold text-center mb-12 glow">About Us</h1>
      <div className="flex flex-wrap justify-center gap-8 max-w-6xl mx-auto px-4" ref={membersRef}>
        {membersData.map((member, index) => (
          <div
            key={index}
            className="relative p-9 bg-gray-800 rounded-lg shadow-2xl w-80 overflow-hidden member-card"
            style={{
              padding: '1px',
              borderRadius: '10px',
              backgroundImage: 'linear-gradient(45deg, #ff0066, #ffcc00, #00ccff, #00ff99)',
              backgroundSize: '200% 200%',
              backgroundClip: 'border-box',
              boxShadow: 'inset 0 0 0 1px rgba(255, 255, 255, 0.5)',
              animation: 'gradient-border 15s ease infinite',
            }}
          >
            <div className="relative p-6 bg-gray-800 rounded-lg overflow-hidden">
              <h2 className="text-2xl font-bold mb-4">{member.name}</h2>
              <p className="text-md text-gray-400 mb-2">{member.role}</p>
              <p className="text-sm mb-4">{member.description}</p>
              {member.instagram && (
                <a
                  href={member.instagram}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-white hover:text-pink-400 transition-colors duration-300"
                >
                  <FaInstagram size={24} />
                  <span className="text-sm">Instagram</span>
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Aboutus;
