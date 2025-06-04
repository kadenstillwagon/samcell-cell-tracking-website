import './CellImageGallery.css'
import { useState, useEffect } from 'react'
import CellImageGalleryBlock from './CellImageGalleryBlock'
import ImageAndSegmentationUpload from './ImageAndSegmentationUpload'
import NewImageButton from './NewImageButton'

/**
 * CellImageGallery Component that displays all images in a project in a gallery fashion
 *
 * @param {string} project - Title of the project
 * @param {list} dates - List of dates of when the images were taken
 * @param {func} onImageGalleryBlockClick - Function that is called when an image is clicked on
 * @returns {React.JSX.Element} - The CellImageGallery element.
 */
function CellImageGallery({ project, dates, onImageGalleryBlockClick }) {

    const [addingNewImage, setAddingNewImage] = useState(false)
    const [windowWidth, setWindowWidth] = useState(window.innerWidth)

    const onNewImageClick = () => {
        setAddingNewImage(true)
    }

    window.addEventListener('resize', () => onWindowUpdate())

    const onWindowUpdate = () => {
        setWindowWidth(window.innerWidth)
    }

    const imageGalleryBlockClicked = (date) => {
        onImageGalleryBlockClick(date)
    }


    if (addingNewImage) {
        return (
            <div>
                <ImageAndSegmentationUpload projectTitle={project}/>
                <div style={{textAlign: 'center', marginTop: "min(2vw, 10px)"}}>
                    <button 
                        onClick={() => setAddingNewImage(false)}
                        style={{
                        fontSize: "min(2vw, 25px)",
                        color: 'white',
                        backgroundColor: 'rgb(250, 50, 50)',
                        paddingLeft: 'min(1vw, 10px)',
                        paddingRight: 'min(1vw, 10px)',
                        paddingTop: 'min(0.5vw, 5px)',
                        paddingBottom: 'min(0.5vw, 5px)',
                        borderWidth: 'min(0.25vw, 2px)',
                        borderRadius: 'min(2vw, 12px)'
                        }}
                    >Cancel</button>
                </div>
            </div>
            
        )
    } else {
        if (windowWidth <= 400) {
            if (dates) {
                return (
                    <div className="image-gallery-container">
                        <NewImageButton onNewImageButtonClicked={onNewImageClick} width={76}/>
                        {dates.map((cellImage, index) => {
                            return (
                                <CellImageGalleryBlock 
                                    project={project}
                                    date={dates[index]}
                                    width={76}
                                    onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                />
                            )
                        })}
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={76}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            }
        } else if (windowWidth > 400 && windowWidth <= 800) {
            if (dates) {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={37}/>
                            {dates.slice(0, 1).map((cellImage, index) => {
                                return (
                                    <CellImageGalleryBlock 
                                        project={project}
                                        date={dates[index]}
                                        width={37}
                                        onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                    />
                                )
                            })}

                        </div>
                        
                        {dates.slice(1, dates.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 2 == 0) {
                                return (
                                    <div className="image-gallery-row">
                                        {dates.slice(indexOne + 1, indexOne + 3).map((cellImage, indexTwo) => {
                                            return (
                                                <CellImageGalleryBlock 
                                                    project={project}
                                                    date={dates[indexTwo + indexOne + 1]}
                                                    width={37}
                                                    onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                                />
                                            )
                                        })}
                                    </div>
                                )
                            }
                        })
                                
                        }
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={37}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else if (windowWidth > 800 && windowWidth <= 1200) {
            if (dates) {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={24}/>
                            {dates.slice(0, 2).map((cellImage, index) => {
                                return (
                                    <CellImageGalleryBlock 
                                        project={project}
                                        date={dates[index]}
                                        width={24}
                                        onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                    />
                                )
                            })}

                        </div>
                        
                        {dates.slice(2, dates.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 3 == 0) {
                                return (
                                    <div className="image-gallery-row">
                                        {dates.slice(indexOne + 2, indexOne + 5).map((cellImage, indexTwo) => {
                                            return (
                                                <CellImageGalleryBlock 
                                                    project={project}
                                                    date={dates[indexTwo + indexOne + 2]}
                                                    width={24}
                                                    onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                                />
                                            )
                                        })}
                                    </div>
                                )
                            }
                        })
                                
                        }
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={24}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else if (windowWidth > 1200 && windowWidth <= 1600) {
            if (dates) {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={17.5}/>
                            {dates.slice(0, 3).map((cellImage, index) => {
                                return (
                                    <CellImageGalleryBlock 
                                        project={project}
                                        date={dates[index]}
                                        width={17.5}
                                        onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                    />
                                )
                            })}

                        </div>
                        
                        {dates.slice(3, dates.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 4 == 0) {
                                return (
                                    <div className="image-gallery-row">
                                        {dates.slice(indexOne + 3, indexOne + 7).map((cellImage, indexTwo) => {
                                            return (
                                                <CellImageGalleryBlock 
                                                    project={project}
                                                    date={dates[indexTwo + indexOne + 3]}
                                                    width={17.5}
                                                    onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                                />
                                            )
                                        })}
                                    </div>
                                )
                            }
                        })
                                
                        }
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={17.5}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else {
            if (dates) {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={13.6}/>
                            {dates.slice(0, 4).map((cellImage, index) => {
                                return (
                                    <CellImageGalleryBlock 
                                        project={project}
                                        date={dates[index]}
                                        width={13.6}
                                        onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                    />
                                )
                            })}

                        </div>
                        
                        {dates.slice(4, dates.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 5 == 0) {
                                return (
                                    <div className="image-gallery-row">
                                        {dates.slice(indexOne + 4, indexOne + 9).map((cellImage, indexTwo) => {
                                            return (
                                                <CellImageGalleryBlock 
                                                    project={project}
                                                    date={dates[indexTwo + indexOne + 4]}
                                                    width={13.6}
                                                    onImageGalleryBlockClick={(date) => imageGalleryBlockClicked(date)}
                                                />
                                            )
                                        })}
                                    </div>
                                )
                            }
                        })
                                
                        }
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="image-gallery-container">
                        <div className='image-gallery-row'>
                            <NewImageButton onNewImageButtonClicked={onNewImageClick} width={13.6}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        }
    }
}

export default CellImageGallery