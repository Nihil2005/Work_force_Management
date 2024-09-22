
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import LoginComponent from './auth/LoginComponent';
import SignupComponent from './auth/SignupComponent';
import EmailActivationComponent from './auth/EmailActivationComponent';
import ProfileComponent from './auth/ProfileComponent';
import Navbar from './pages/Navbar';
import Attendance from './auth/Attendance';
import Performance from './auth/Performance';
import Shifts from './auth/Shifts';
import Homepage from './pages/Homepage';
import Aboutus from './pages/Aboutus';
import Contact from './pages/Contact';
const App = () => {
  
  

  return (
    <div>
      <BrowserRouter>
        <Navbar />
      

        <Routes>

          <Route path="/home" element={<Homepage/>}/>
          <Route path="/login" element={<LoginComponent />} />
          <Route path="/signup" element={<SignupComponent />} />
          <Route path="/activate" element={<EmailActivationComponent />} />
          <Route path="/profile" element={<ProfileComponent/>} />
          <Route path='/profile/attendence' element={<Attendance/>} />
          <Route path='/profile/performanace' element={<Performance/>}/>
          <Route path='/profile/shifts' element={<Shifts/>}/>
          <Route path='about-us' element={<Aboutus/>}/>
          <Route path='/contact-us' element={<Contact/>}/>
        
       
     
 
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default App;
