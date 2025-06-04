import './CellImageGalleryBlock.css'
import { useState, useEffect } from 'react'

/**
 * CellImageGalleryBlock Component that displays an image, the captured date on hover, and can
 * be clicked to plot the metrics of the single image
 *
 * @param {string} project - Title of the project
 * @param {string} date - Date of the image in the block
 * @param {int} width - width of the block
 * @param {func} onImageGalleryBlockClick - Function that is called when an image is clicked on
 * @returns {React.JSX.Element} - The CellImageGalleryBlock element.
 */
function CellImageGalleryBlock({ project, date, width, onImageGalleryBlockClick }) {
    const [isHovering, setIsHovering] = useState(false);
    const [blockImage, setBlockImage] = useState()

    useEffect(() => {
        const formData = new FormData()
        formData.append('Project', project)
        formData.append('Date', date)

        fetch('/get_specific_image', {method: 'POST', body: formData}).then(
            res => res.blob()
        ).then(
            blob => {
                setBlockImage(URL.createObjectURL(blob))
            }
        )

    }, [])


    if (isHovering) {
        return (
            <div className="image-gallery-block-container" style={{width: `${width}vw`, height: `${width * (2/3)}vw`}} onMouseLeave={() => setIsHovering(false)} onClick={() => onImageGalleryBlockClick(date)}>
                <img 
                    src={blockImage} 
                    alt={date}
                    style={{
                        width: "100%",
                        height: "100%"
                    }}
                />
                <div style={{backgroundColor: "rgb(60, 60, 60)", height: `${width * (1/6)}vw`, marginTop: `-${width * (1.1/6)}vw`, opacity: "60%", textAlign: "center"}}>
                    <div style={{fontSize: `${width * (1/16)}vw`, color: "rgb(255, 254, 240)", paddingTop: `${width * (1/20)}vw`}}>{date}</div>
                </div>
            </div>
        )    
    } else {
        return (
            <div className="image-gallery-block-container" style={{width: `${width}vw`, height: `${width * (2/3)}vw`}} onMouseEnter={() => setIsHovering(true)} onClick={() => onImageGalleryBlockClick(date)}>
                <img 
                    src={blockImage} 
                    alt={date}
                    style={{
                        width: "100%",
                        height: "100%"
                    }}
                />
            </div>
        )
    }
        
}

export default CellImageGalleryBlock