import React, { useState } from 'react'
import './NewProjectButton.css'

function NewProjectButton({ onNewProjectButtonClicked, width }) {
    const [isHovering, setIsHovering] = useState(false)

  return (
    <div 
        className="new-project-button" 
        style={{
            fontSize: `${width * (1/2.4)}vw`, 
            backgroundColor: (isHovering) ? "rgb(120, 120,120)" : "rgb(160, 160, 160)", 
            width: `${width - (width * 2/20)}vw`, 
            height: `${width * (8.3/10)}vw`,
            paddingTop: `${width * (1.1/4)}vw`,
            paddingLeft: `${width * (1/20)}vw`,
            paddingRight: `${width * (1/20)}vw`
        }} 
        onClick={onNewProjectButtonClicked} 
        onMouseEnter={() => setIsHovering(true)} 
        onMouseLeave={() => setIsHovering(false)}
    >+</div>
  )
}

export default NewProjectButton