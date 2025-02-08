import React, { useState } from 'react';
import { BarChart2, ChevronDown } from 'lucide-react';

const NavMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <div 
        className="nav-item flex items-center cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <BarChart2 className="nav-icon" />
        <span>Stock & fund</span>
        <ChevronDown className={`ml-auto transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </div>
      
      {isOpen && (
        <>
          <div className="nav-sub-item">Stock</div>
          <div className="nav-sub-item">Cryptocurrency</div>
          <div className="nav-sub-item">Mutual Fund</div>
          <div className="nav-sub-item">Gold</div>
        </>
      )}
    </div>
  );
};

export default NavMenu;