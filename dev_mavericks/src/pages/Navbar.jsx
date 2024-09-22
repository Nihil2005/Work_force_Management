import React, { useState } from "react";
import { MenuIcon, UserCircleIcon } from "@heroicons/react/solid";
import axios from "axios";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  

  return (
    <div>
      <nav className="bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <a href="/home">
                <img 
                  className="h-auto w-32 md:w-48 mx-auto mt-2"
                  src="public/lox.png"
                  alt="logo"
                />
              </a>
              <div>
              </div>
              <div className="hidden md:block ml-9">
                <a
                  href="/home"
                  className="text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                >
                  Home
                </a>
                <a
                  href="/login"
                  className="text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                >
                  Login
                </a>
                <a
                  href="/signup"
                  className="text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                >
                  Signup
                </a>
                <a href="/about-us" className="text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700">
                  About Us
                </a>
                <a href="/contact-us" className="text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700">
                 Contact Us
                </a>
               
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              
              <a href="/profile">
                <UserCircleIcon className="h-6 w-6 text-white" />
              </a>
            </div>
            <div className="-mr-2 flex md:hidden">
              <button
                onClick={toggleMenu}
                className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-gray-700 focus:outline-none focus:bg-gray-700"
              >
                <MenuIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>
      </nav>
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-red-400">
            <a
              href="#"
              className="text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
            >
              Home
            </a>
            <a
              href="#"
              className="text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
            >
              Login
            </a>
            <a
              href="#"
              className="text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
            >
              Signup
            </a>
            <a
              href="#"
              className="text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
            >
              About Us
            </a>
            <a
              href="#"
              className="text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
            >
              Contact Us
            </a>
          </div>
          <div className="px-2 pt-2 pb-3 sm:px-3 bg-black">
          </div>
        </div>
      )}

    </div>
  );
};    


export default Navbar;