import React from 'react'
import { useState } from 'react'

function ProjectNavigationBar({ onPageSelection }) {

    const [gallerySelected, setGallerySelected] = useState(true)

    const backgroundColor = 'rgb(53, 53, 153)'

    const pageSelected = (page) => {
        onPageSelection(page)
        if (page == "Image Gallery") {
            setGallerySelected(true)
        } else {
            setGallerySelected(false)
        }
    }


  return (
    <div style={{width: "100vw", textAlign: 'center', backgroundColor: backgroundColor, height: 'min(8vw, 50px)', boxShadow: 'rgb(61, 61, 61) 0px 1px 5px'}}>
        <div style={{display: "flex", justifySelf: 'center', width: "min(40vw, 400px)", height: 'min(8vw, 50px)', textAlign: 'center'}}>
            <button style={{
                color: (gallerySelected) ? "rgb(250, 250, 250)" : "rgb(182, 182, 182)", 
                width: 'min(20vw, 200px)', 
                backgroundColor: backgroundColor, 
                fontSize: 'min(2.2vw, 18px)', 
                marginTop: 'min(1vw, 1px)', 
                borderRightWidth: '0px', 
                borderLeftWidth: '0px', 
                borderTopWidth: "0px", 
                borderBottomWidth: (gallerySelected) ? "min(0.8vw, 4px)" : "0px", 
                borderColor: 'orange',
                marginRight: 'min(2vw, 15px)'
            }}
            onClick={() => pageSelected("Image Gallery")}
            >Image Gallery</button>
            <button style={{
                color: (!gallerySelected) ? "rgb(250, 250, 250)" : "rgb(182, 182, 182)", 
                width: 'min(20vw, 200px)', 
                backgroundColor: backgroundColor, 
                fontSize: 'min(2.2vw, 18px)', 
                marginTop: 'min(1vw, 1px)', 
                borderRightWidth: '0px', 
                borderLeftWidth: '0px', 
                borderTopWidth: "0px", 
                borderBottomWidth: (!gallerySelected) ? "min(0.8vw, 4px)" : "0px", 
                borderColor: 'orange',
                marginLeft: 'min(2vw, 15px)'
            }}
            onClick={() => pageSelected("Metric Tracking")}
            >Metric Tracking</button>
        </div>
        
    </div>
  )
}

export default ProjectNavigationBar