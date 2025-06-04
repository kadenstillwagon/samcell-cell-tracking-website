import React, { useState } from 'react'
import './NewImageButton.css'

function NewImageButton({ onNewImageButtonClicked, width }) {
    const [isHovering, setIsHovering] = useState(false)

  return (
    <div className="new-image-button" style={{fontSize: `${width * (1/2.4)}vw`, backgroundColor: (isHovering) ? "rgb(120, 120,120)" : "rgb(160, 160, 160)", width: `${width}vw`, height: `${width * (2/3) - (width * (1/24))}vw`, paddingTop: `${width * (1/24)}vw`}} onClick={onNewImageButtonClicked} onMouseEnter={() => setIsHovering(true)} onMouseLeave={() => setIsHovering(false)}>+</div>
  )
}

export default NewImageButton