import './ProjectBlock.css'
import BlankImage from '../BlankImage.png'
import { useState, useEffect } from 'react';

function ProjectBlock({ projectImage, projectTitle, projectDescription, onProjectBlockClick, width }) {
    const [isHovering, setIsHovering] = useState(false);

    const [displayTitle, setDisplayTitle] = useState(projectTitle)
    const [displayImage, setDisplayImage] = useState()
    const [displayDescription, setDisplayDescription] = useState(projectDescription)


    useEffect(() => {
        if (projectTitle.length > 40) {
            setDisplayTitle(projectTitle.slice(0, 37) + '...')
        }
        if (projectDescription.length > 50) {
            setDisplayDescription(projectDescription.slice(0, 47) + '...')
        }
    }, [])

    useEffect(() => {
        if (projectImage != 'None') {
            const formData = new FormData()
            formData.append('Project', projectTitle)

            fetch('/get_cover_image', {
                method: 'POST', 
                body: formData
            }).then(
                res => res.blob()
            ).then(
                blob => {
                    setDisplayImage(URL.createObjectURL(blob))
                }
            )
        } 
    }, [])

    if (!displayImage) {
        return (
            <div 
                className="project-block-container" 
                onClick={e => onProjectBlockClick(e, projectTitle) } 
                style={{
                    backgroundColor: (isHovering) ? "rgb(120, 120,120)" : "rgb(160, 160, 160)", 
                    width: `${width  - (width * 2/20)}vw`, 
                    
                    paddingTop: `${width * (1/20)}vw`,
                    paddingLeft: `${width * (1/20)}vw`,
                    paddingRight: `${width * (1/20)}vw`,
                    paddingBottom: `${width * (1/20)}vw`,
                }} 
                onMouseEnter={() => setIsHovering(true)} 
                onMouseLeave={() => setIsHovering(false)}
            >
                <img 
                    src={BlankImage} 
                    alt={"Logo"}
                    style={{
                        width: "100%",
                        height: `${width * (1.92/3)}vw`
                    }}
                />
                <div className='project-description-text' style={{fontSize: `${width * (1/11)}vw`, marginTop: "0vw", color:"rgb(20, 20, 20)", overflow: 'hidden'}}>{displayTitle}</div>
                <div className='project-description-text' style={{fontSize: `${width * (1/18)}vw`, marginTop: "0vw", color:"rgb(20, 20, 20)", overflow: 'hidden'}}>{displayDescription}</div>
            </div>
        )
    } else {
        return (
            <div 
                className="project-block-container" 
                onClick={e => onProjectBlockClick(e, projectTitle) } 
                style={{
                    backgroundColor: (isHovering) ? "rgb(120, 120,120)" : "rgb(160, 160, 160)", 
                    width: `${width - (width * 2/20)}vw`, 
                    
                    paddingTop: `${width * (1/20)}vw`,
                    paddingLeft: `${width * (1/20)}vw`,
                    paddingRight: `${width * (1/20)}vw`,
                    paddingBottom: `${width * (1/20)}vw`
                }} 
                onMouseEnter={() => setIsHovering(true)} 
                onMouseLeave={() => setIsHovering(false)}
            >                <img 
                    src={displayImage} 
                    alt={"Logo"}
                    style={{
                        width: "100%",
                        height: `${width * (1.92/3)}vw`
                    }}
                />
                <div className='project-description-text' style={{fontSize: `${width * (1/11)}vw`, marginTop: "0vw", color:"rgb(20, 20, 20)", overflow: 'hidden'}}>{displayTitle}</div>
                <div className='project-description-text' style={{fontSize: `${width * (1/18)}vw`, marginTop: "0vw", color:"rgb(20, 20, 20)"}}>{displayDescription}</div>
            </div>
        )
    }
  
}

export default ProjectBlock