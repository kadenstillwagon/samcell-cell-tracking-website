import './ImageAndSegmentationUpload.css'
import { useState, useRef, use } from 'react'
import SingleOrMultiUploadSelection from './SingleOrMultiUploadSelection'

function ImageAndSegmentationUpload({ projectTitle, onCancelClicked }) {

    const [image, setImage] = useState()
    const [imageUploaded, setImageUploaded] = useState(false)
    const [csvUploaded, setCsvUploaded] = useState(false)
    const [dateUploaded, setDateUploaded] = useState(false)

    const [singleSelected, setSingleSelected] = useState(true)

    const [imagesUploaded, setImagesUploaded] = useState(false)
    const [namesUploaded, setNamesUploaded] = useState(false)
    const [annotationsUploaded, setAnnotationsUploaded] = useState(false)

    const imageInputRef = useRef()
    const csvInputRef = useRef()
    const dateInputRef = useRef()
    const imagesInputRef = useRef()
    const namesInputRef = useRef()
    const annotationsInputRef = useRef()

    const [isHovering, setIsHovering] = useState(false)

    const handleOnImageChange = (event) => {
        if (event.target.files[0]) {
            console.log(event.target.files[0])
            setImage(URL.createObjectURL(event.target.files[0]))
            setImageUploaded(true)
        } else {
            console.log("Input Cancelled")
            setImage()
            setImageUploaded(false)
        }
      }

      const handleOnCsvChange = (event) => {
        if (event.target.files[0]) {
            console.log(event.target.files[0])
            setCsvUploaded(true)
        } else {
            console.log("Input Cancelled")
            setCsvUploaded(false)
        }
      }

      const handleOnDateChange = (event) => {
        if (event.target.value) {
            console.log(event.target.value)
            setDateUploaded(true)
        } else {
            console.log("Input Cancelled")
            setDateUploaded(false)
        }
      }

      const handleOnImagesChange = (event) => {
        if (event.target.files[0]) {
            console.log(event.target.files[0])
            setImagesUploaded(true)
        } else {
            console.log("Input Cancelled")
            setImagesUploaded(false)
        }
      }

      const handleOnNamesChange = (event) => {
        if (event.target.files[0]) {
            console.log(event.target.files[0])
            setNamesUploaded(true)
        } else {
            console.log("Input Cancelled")
            setNamesUploaded(false)
        }
      }

      const handleOnAnnotationsChange = (event) => {
        if (event.target.files[0]) {
            console.log(event.target.files[0])
            setAnnotationsUploaded(true)
        } else {
            console.log("Input Cancelled")
            setAnnotationsUploaded(false)
        }
      }

    const handleOnSubmit = (e) => {
        e.preventDefault();
    
        if (singleSelected) {
            const formData = new FormData(e.target);
            console.log(projectTitle)
            formData.append("Project", projectTitle)
            console.log(e.target)
            console.log(formData)
            console.log(formData.get('image'))
            console.log(formData.get('segmentation_csv'))
            console.log(formData.get('date-time'))
            console.log(formData.get('Project'))
        
            fetch('/upload_image', {
            method: 'POST',
            body: formData
            }).then(res => {
                res.json().then(data => {console.log(data)})
            })
        } else {
            const formData = new FormData(e.target);
            console.log(projectTitle)
            formData.append("Project", projectTitle)
            console.log(e.target)
            console.log(formData)
            console.log(formData.get('images'))
            console.log(formData.get('names'))
            console.log(formData.get('annotations'))
            console.log(formData.get('Project'))
        
            fetch('/upload_many_images', {
            method: 'POST',
            body: formData
            }).then(res => {
                res.json().then(data => {console.log(data)})
            })
        }
            

        if (imageInputRef.current) {
            imageInputRef.current.value = "";
        }
        if (csvInputRef.current) {
            csvInputRef.current.value = "";
        }
        if (dateInputRef.current) {
            dateInputRef.current.value = "";
        }
        if (imagesInputRef.current) {
            imagesInputRef.current.value = "";
        }
        if (namesInputRef.current) {
            namesInputRef.current.value = "";
        }
        if (annotationsInputRef.current) {
            annotationsInputRef.current.value = "";
        }
        setImage()
        setImageUploaded(false)
        setCsvUploaded(false)
        setDateUploaded(false)
        setImagesUploaded(false)
        setNamesUploaded(false)
        setAnnotationsUploaded(false)
    }

    const onSingleClick = () => {
        setSingleSelected(true)
        setImagesUploaded(false)
        setNamesUploaded(false)
        setAnnotationsUploaded(false)
        if (imagesInputRef.current) {
            imagesInputRef.current.value = "";
        }
        if (namesInputRef.current) {
            namesInputRef.current.value = "";
        }
        if (annotationsInputRef.current) {
            annotationsInputRef.current.value = "";
        }
    }

    const onMultiClick = () => {
        setSingleSelected(false)
        setImage()
        setImageUploaded(false)
        setCsvUploaded(false)
        setDateUploaded(false)
        if (imageInputRef.current) {
            imageInputRef.current.value = "";
        }
        if (csvInputRef.current) {
            csvInputRef.current.value = "";
        }
        if (dateInputRef.current) {
            dateInputRef.current.value = "";
        }
    }


    if (singleSelected) {
        if (imageUploaded && csvUploaded) {
            return (      
                <div>
                    <SingleOrMultiUploadSelection onSingleClick={onSingleClick} onMultiClick={onMultiClick} selectedButton={'Single'}/>
                    <div className="image-and-segmentation-upload-container">
                        <div style={{fontSize: "min(3.5vw, 40px)", paddingTop: "min(2vw, 20px)", textAlign: "center"}}>Upload New Image</div>
                        <img 
                            src={image} 
                            onClick={() => imageInputRef.current.click()}
                            style={{
                                width: "min(54vw, 515px)",
                                height: "min(36vw, 300px)",
                                marginLeft: "min(3vw, 30px)",
                                marginTop: "min(2vw, 20px)",
                                backgroundColor: (isHovering) ? "rgb(143, 143, 143)" : "rgb(163, 163, 163)"
                            }}
                        />
                        <form onSubmit={handleOnSubmit} >
                            <div style={{display: "flex", marginLeft: "min(3vw, 30px)", paddingBottom: "min(2vw, 15px)", paddingTop: "min(1vw, 20px)"}}>
                                <div style={{fontSize: "min(1.8vw, 20px)", paddingBottom: "min(1vw, 20px)"}}>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>Image Upload: </div>
                                    <div style={{marginBottom: "min(1vw, 20px)"}}>Segmentation Upload: </div>
                                    <div>Date/Time Image Taken: </div>
                                </div>
        
                                <div style={{marginLeft: "min(2vw, 20px)", fontSize: "min(1.8vw, 20px)"}}>
                                    
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="image" 
                                            accept="image/*"
                                            ref={imageInputRef}
                                            onChange={(e) => handleOnImageChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="segmentation_csv" 
                                            accept=".csv"
                                            ref={csvInputRef}
                                            onChange={(e) => handleOnCsvChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div>
                                        <input 
                                            type="datetime-local" 
                                            name="date-time" 
                                            ref={dateInputRef}
                                            onChange={(e) => handleOnDateChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)"}}
                                        />
                                    </div>
                                </div>
                            </div>
                            <div style={{ width: "min(60vw, 575px)", textAlign: "right"}}>
                                <button 
                                    type="submit"
                                    style={{
                                        fontSize: "min(1.8vw, 18px)",
                                        width: "min(12vw, 80px)",
                                        height: "min(4vw, 45px)",
                                        borderRadius: "min(1vw, 12px)",
                                        marginBottom: "min(2vw, 20px)",
                                        marginRight: "min(2vw, 20px)",
                                        backgroundColor: "rgb(160, 160, 160)"
                                    }}
                                
                                >Upload</button>
                            </div>
                        </form>
                    </div>
                </div>
            )
        } else if (imageUploaded) {
            return (
                <div>
                    <SingleOrMultiUploadSelection onSingleClick={onSingleClick} onMultiClick={onMultiClick} selectedButton={'Single'}/>
                    <div className="image-and-segmentation-upload-container">
                        <div style={{fontSize: "min(3.5vw, 40px)", paddingTop: "min(2vw, 20px)", textAlign: "center"}}>Upload New Image</div>
                        <img 
                            src={image} 
                            onClick={() => imageInputRef.current.click()}
                            style={{
                                width: "min(54vw, 515px)",
                                height: "min(36vw, 300px)",
                                marginLeft: "min(3vw, 30px)",
                                marginTop: "min(2vw, 20px)",
                                backgroundColor: (isHovering) ? "rgb(143, 143, 143)" : "rgb(163, 163, 163)"
                            }}
                        />
                        <form onSubmit={handleOnSubmit} >
                            <div style={{display: "flex", marginLeft: "min(3vw, 30px)", paddingBottom: "min(2vw, 15px)", paddingTop: "min(1vw, 20px)"}}>
                                <div style={{fontSize: "min(1.8vw, 20px)", paddingBottom: "min(1vw, 20px)"}}>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>Image Upload: </div>
                                    <div style={{marginBottom: "min(1vw, 20px)"}}>Segmentation Upload: </div>
                                    <div>Date/Time Image Taken: </div>
                                </div>
        
                                <div style={{marginLeft: "min(2vw, 20px)", fontSize: "min(1.8vw, 20px)"}}>
                                    
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="image" 
                                            accept="image/*"
                                            ref={imageInputRef}
                                            onChange={(e) => handleOnImageChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="segmentation_csv" 
                                            accept=".csv"
                                            ref={csvInputRef}
                                            onChange={(e) => handleOnCsvChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div>
                                        <input 
                                            type="datetime-local" 
                                            name="date-time" 
                                            ref={dateInputRef}
                                            onChange={(e) => handleOnDateChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)"}}
                                        />
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                
            )
        } else {
            return (
                <div>
                    <SingleOrMultiUploadSelection onSingleClick={onSingleClick} onMultiClick={onMultiClick} selectedButton={'Single'}/>
                    <div className="image-and-segmentation-upload-container">
                        <div style={{fontSize: "min(3.5vw, 40px)", paddingTop: "min(2vw, 20px)", textAlign: "center"}}>Upload New Image</div>
                        <div 
                            onClick={() => imageInputRef.current.click()}
                            onMouseEnter={() => setIsHovering(true)}
                            onMouseLeave={() => setIsHovering(false)}
                            style={{
                                width: "min(54vw, 515px)",
                                height: "min(36vw, 300px)",
                                marginLeft: "min(3vw, 30px)",
                                marginTop: "min(2vw, 20px)",
                                backgroundColor: (isHovering) ? "rgb(143, 143, 143)" : "rgb(163, 163, 163)"
                            }}
                        >
                        <div style={{fontSize: "min(2vw, 22px)", textAlign: "center", color: "black", paddingTop: "min(16vw, 130px)"}}>Click Here to Upload</div>
                    </div>
                    <form onSubmit={handleOnSubmit} >
                        <div style={{display: "flex", marginLeft: "min(3vw, 30px)", paddingBottom: "min(2vw, 15px)", paddingTop: "min(1vw, 20px)"}}>
                            <div style={{fontSize: "min(1.8vw, 20px)", paddingBottom: "min(1vw, 20px)"}}>
                                <div style={{marginBottom: "min(1vw, 15px)"}}>Image Upload: </div>
                                <div style={{marginBottom: "min(1vw, 20px)"}}>Segmentation Upload: </div>
                                <div>Date/Time Image Taken: </div>
                            </div>
    
                            <div style={{marginLeft: "min(2vw, 20px)", fontSize: "min(1.8vw, 20px)"}}>
                                    
                                <div style={{marginBottom: "min(1vw, 15px)"}}>
                                    <input 
                                        type="file" 
                                        name="image" 
                                        accept="image/*"
                                        ref={imageInputRef}
                                        onChange={(e) => handleOnImageChange(e)}
                                        style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                    />
                                </div>
                                <div style={{marginBottom: "min(1vw, 15px)"}}>
                                    <input 
                                        type="file" 
                                        name="segmentation_csv" 
                                        accept=".csv"
                                        ref={csvInputRef}
                                        onChange={(e) => handleOnCsvChange(e)}
                                        style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                    />
                                </div>
                                <div>
                                    <input 
                                        type="datetime-local" 
                                        name="date-time" 
                                        ref={dateInputRef}
                                        onChange={(e) => handleOnDateChange(e)}
                                        style={{fontSize: "min(1.4vw, 15px)"}}
                                    />
                                </div>
                            </div>
                        </div>
                    </form>
                    </div>
                </div>
                
            )
        }
    } else {
        if (imagesUploaded && namesUploaded && annotationsUploaded) {
            return (      
                <div>
                    <SingleOrMultiUploadSelection onSingleClick={onSingleClick} onMultiClick={onMultiClick} selectedButton={'Multi'}/>
                    <div className="image-and-segmentation-upload-container">
                        <div style={{fontSize: "min(3.5vw, 40px)", paddingTop: "min(2vw, 20px)", textAlign: "center"}}>Upload New Images</div>
                        <form onSubmit={handleOnSubmit} style={{backgroundColor: "rgb(163, 163, 163)", margin: "min(2vw, 20px)"}}>
                            <div style={{display: "flex", marginLeft: "min(3vw, 30px)", paddingBottom: "min(2vw, 15px)", paddingTop: "min(1vw, 20px)"}}>
                                <div style={{fontSize: "min(1.8vw, 20px)", paddingBottom: "min(1vw, 20px)"}}>
                                    <div style={{marginBottom: "min(1.3vw, 13px)"}}>Images Array Upload: </div>
                                    <div style={{marginBottom: "min(1.3vw, 13px)"}}>Names Array Upload: </div>
                                    <div>Annotations Array Upload: </div>
                                </div>
        
                                <div style={{marginLeft: "min(2vw, 20px)", fontSize: "min(1.8vw, 20px)"}}>
                                    
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="images" 
                                            accept=".npy"
                                            ref={imagesInputRef}
                                            onChange={(e) => handleOnImagesChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="names" 
                                            accept=".npy"
                                            ref={namesInputRef}
                                            onChange={(e) => handleOnNamesChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div>
                                        <input 
                                            type="file" 
                                            name="annotations" 
                                            accept=".npy"
                                            ref={annotationsInputRef}
                                            onChange={(e) => handleOnAnnotationsChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                </div>
                            </div>
                            <div style={{ width: "min(60vw, 575px)", textAlign: "center"}}>
                                <button 
                                    type="submit"
                                    style={{
                                        fontSize: "min(1.8vw, 18px)",
                                        width: "min(12vw, 80px)",
                                        height: "min(4vw, 45px)",
                                        borderRadius: "min(1vw, 12px)",
                                        marginBottom: "min(2vw, 20px)",
                                        marginRight: "min(4vw, 40px)",
                                        backgroundColor: "rgb(210, 210, 210)"
                                    }}
                                >Upload</button>
                            </div>
                        </form>
                        <div style={{backgroundColor: "rgb(210, 210, 210)", height: "min(2vw, 20px)"}}/>
                    </div>
                </div>
            )
        } else {
            return (
                <div>
                    <SingleOrMultiUploadSelection onSingleClick={onSingleClick} onMultiClick={onMultiClick} selectedButton={'Multi'}/>
                    <div className="image-and-segmentation-upload-container">
                        <div style={{fontSize: "min(3.5vw, 40px)", paddingTop: "min(2vw, 20px)", textAlign: "center"}}>Upload New Images</div>
                        <form onSubmit={handleOnSubmit} style={{backgroundColor: "rgb(163, 163, 163)", margin: "min(2vw, 20px)"}}>
                            <div style={{display: "flex", marginLeft: "min(3vw, 30px)", paddingBottom: "min(2vw, 15px)", paddingTop: "min(1vw, 20px)"}}>
                                <div style={{fontSize: "min(1.8vw, 20px)", paddingBottom: "min(1vw, 20px)", marginTop: "min(1vw, 10px)"}}>
                                    <div style={{marginBottom: "min(1.3vw, 13px)"}}>Images Array Upload: </div>
                                    <div style={{marginBottom: "min(1.3vw, 13px)"}}>Names Array Upload: </div>
                                    <div >Annotations Array Upload: </div>
                                </div>
        
                                <div style={{marginLeft: "min(2vw, 20px)", fontSize: "min(1.8vw, 20px)"}}>
                                    
                                    <div style={{marginBottom: "min(1vw, 15px)", marginTop: "min(1vw, 10px)"}}>
                                        <input 
                                            type="file" 
                                            name="images" 
                                            accept=".npy"
                                            ref={imagesInputRef}
                                            onChange={(e) => handleOnImagesChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div style={{marginBottom: "min(1vw, 15px)"}}>
                                        <input 
                                            type="file" 
                                            name="names" 
                                            accept=".npy"
                                            ref={namesInputRef}
                                            onChange={(e) => handleOnNamesChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                    <div>
                                        <input 
                                            type="file" 
                                            name="annotations" 
                                            accept=".npy"
                                            ref={annotationsInputRef}
                                            onChange={(e) => handleOnAnnotationsChange(e)}
                                            style={{fontSize: "min(1.4vw, 15px)", color: 'rgb(250, 50, 50)'}}
                                        />
                                    </div>
                                </div>
                            </div>
                        </form>
                        <div style={{fontSize: "15px", padding: "min(3vw, 30px)", paddingTop: "0px"}}>
                            <div style={{fontWeight: "600"}}>NOTE: Items MUST be in order such that the image at index 0 corresponds to the name at index 0 and the annotation at index 0.</div>
                        </div>
                    </div>
                </div>
            )
        }
    }
    
        
}

export default ImageAndSegmentationUpload