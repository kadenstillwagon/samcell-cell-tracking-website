import React, { useEffect, useState } from 'react'
import './NewProjectInput.css'

function NewProjectInput({ passDataToParent }) {

    const [projectTitle, setProjectTitle] = useState()
    const [projectDescription, setProjectDescription] = useState()

    const onTitleChange = (e) => {
        //console.log(e.target.value)
        setProjectTitle(e.target.value)
    }


    const onDescriptionChange = (e) => {
        //console.log(e.target.value)
        setProjectDescription(e.target.value)
    }

    const onSubmit = (e) => {
        e.preventDefault(); 

        passDataToParent({'Title': projectTitle, 'Description': projectDescription})
    }

    

  return (
    <div className='new-project-input-container'>
        <div style={{textAlign: 'center', fontSize: 'min(3vw, 40px)', fontColor: 'rgb(81, 81, 81)', fontWeight: '600'}}>Create New Project</div>
        <form onSubmit={(e) => onSubmit(e)} style={{backgroundColor: 'rgb(71, 71, 71)', padding: 'min(2vw, 20px)', marginTop: "min(1vw, 10px)"}} >
            <div style={{display: 'flex'}}>   
                <div style={{fontSize: 'min(2.3vw, 30px)', marginRight: 'min(1vw, 15px)', fontWeight: '600'}}>Title: </div>
                    <div style={{marginBottom: "min(1vw, 10px)"}}>
                        <textarea 
                            id="project-title" 
                            placeholder='Project Title'
                            maxLength={40}
                            onChange={(e) => onTitleChange(e)}
                            style={{resize: 'none', fontSize: "min(1.4vw, 20px)", color: 'rgb(210, 210, 210)', width: 'min(47.5vw, 660px)', height: 'min(2.3vw, 30px)', textAlign: 'top', backgroundColor: 'rgb(51, 51, 51)', paddingTop: 'min(0.7vw, 7px)'}}
                        />
                    </div>
            </div>
            
            <div style={{display: 'flex'}}>   
                <div style={{fontSize: 'min(2.3vw, 30px)', marginRight: 'min(1vw, 15px)', fontWeight: '600'}}>Description: </div>
                <div style={{marginBottom: "min(1vw, 10px)"}}>
                    <textarea 
                        id="project-description" 
                        placeholder='Project Description'
                        maxLength={200}
                        onChange={(e) => onDescriptionChange(e)}
                        style={{resize: 'none', fontSize: "min(1.4vw, 20px)", color: 'rgb(210, 210, 210)', width: 'min(40vw, 562px)', height: 'min(10vw, 150px)', textAlign: 'top', backgroundColor: 'rgb(51, 51, 51)'}}
                    />
                </div>
            </div>

            <div style={{justifySelf: 'center'}}>
                <button 
                    type="submit"
                    style={{
                        fontSize: "min(1.8vw, 25px)",
                        width: "min(56vw, 760px)",
                        height: "min(4vw, 60px)",
                        borderRadius: "min(1vw, 15px)",
                        backgroundColor: "rgb(180, 180, 180)"
                    }}
                >Create Project</button>
            </div>            
            
        </form>
    </div>
  )
}

export default NewProjectInput