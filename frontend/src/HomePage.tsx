import {BarChart2} from 'lucide-react'
import './HomePage.css';
import stockVideo from "./assets/video/Pinterest media.mp4";
import imageLogo from "./assets/photo/reliance.logo.webp"
function HomePage() {

    return(
        <div className='HomePage-mainContainer'>
            <div className='HomePage-container1'>
                <div className='container1-left'>
                    <div className="HomePage-logo-container">
                        <BarChart2 className="nav-icon" />
                        <span className="logo-text">GoStock</span>
                     </div>
                     <div className='left-textline1'>Make Better</div>
                     <div className='left-textline2'>Investment</div>
                     <div className='left-textline3'>Make Better</div>
                     <div className='left-textline4'>Decisions With</div>
                     <div className='left-textline5'>Alternative</div>
                     <div className='left-textline6'>Data.</div>
                     <div className='left-textline7'>Get the inside scoop on companies like</div>
                     <div className='left-textline8'>nerver before.</div>
                </div>

                <div className='container1-center'>
                    <div className='center1'>
                        <img className='image-rel' src={imageLogo} width="100"></img>
                        <span className='id1'>Reliance -1.03%</span>
                    </div>
                    <div className='centre2'>
                        <span className='id2'>₹1,253</span>
                        <span className='id4'>.65</span>
                        <div className='id3'> 🔻-13.05 </div>
                    </div>
                    
                </div>

                <div className='container1-right'>
                    <button className='Login-Button'>
                    Log in
                    </button>
                    <div className='video-Container'>
                        <video width="600" height="750" autoPlay loop muted >
                            <source src={stockVideo} type="video/mp4" />
                        </video>
                    </div>
                    
                </div>
            </div>
            <div className='HomePage-container2'>

            </div>
        </div>
    )



}

export default HomePage;