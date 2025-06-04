import './ProjectsGrid.css'
import { useState, useEffect } from 'react'
import ProjectsBlock from './ProjectBlock'
import NewProjectButton from './NewProjectButton'
import NewProjectInput from './NewProjectInput'

function ProjectsGrid({ onProjectBlockClick }) {

    const [projectImages, setProjectImages] = useState([])
    const [projectTitles, setProjectTitles] = useState([])
    const [projectDescriptions, setProjectDescriptions] = useState([])

    const [addingNewProject, setAddingNewProject] = useState(false)

    const [windowWidth, setWindowWidth] = useState(window.innerWidth)

    window.addEventListener('resize', () => onWindowUpdate())

    const onWindowUpdate = () => {
        setWindowWidth(window.innerWidth)
    }

    useEffect(() => {
        fetch('/get_projects_data').then(
            res => res.json()
        ).then(
            data => {
                console.log(data)
                setProjectImages(data['Project Images'])
                setProjectTitles(data['Project Titles'])
                setProjectDescriptions(data['Project Descriptions'])
            }
        )
        
    }, [])



    

    const onNewProjectButtonClick = () => {
        setAddingNewProject(true)
    }

    const passDataToParent = (newProjectData) => {
        console.log(newProjectData)

        const formData = new FormData()
        for (var key in newProjectData) {
            formData.append(key, newProjectData[key])
        }

        fetch('/add_new_project', {method: 'POST', body: formData}).then(
            res => {
                res.json().then(data => {console.log(data)})
            }
        )

        setAddingNewProject(false)

        fetch('/get_projects_data').then(
            res => res.json()
        ).then(
            data => {
                console.log(data)
                setProjectImages(data['Project Images'])
                setProjectTitles(data['Project Titles'])
                setProjectDescriptions(data['Project Descriptions'])
            }
        )
    }

    if (addingNewProject) {
        return (
            <div>
                <NewProjectInput passDataToParent={passDataToParent}/>
                <div style={{textAlign: 'center', marginTop: "min(2vw, 10px)"}}>
                    <button 
                        onClick={() => setAddingNewProject(false)}
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
            if (projectImages) {
                return (
                    <div className="project-grid-container">
                        <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={76}/>
                        {projectImages.map((cellImage, index) => {
                            return (
                                <ProjectsBlock 
                                    projectTitle={projectTitles[index]}
                                    projectImage={projectImages[index]}
                                    projectDescription={projectDescriptions[index]}
                                    onProjectBlockClick={onProjectBlockClick}
                                    width={76}
                                />
                            )
                        })}
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } else {
                return (
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={76}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            }
        } else if (windowWidth > 400 && windowWidth <= 800) {
            if (projectImages) {
                return (
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={37}/>
                            {projectImages.slice(0, 1).map((cellImage, index) => {
                                return (
                                    <ProjectsBlock 
                                        projectTitle={projectTitles[index]}
                                        projectImage={projectImages[index]}
                                        projectDescription={projectDescriptions[index]}
                                        onProjectBlockClick={onProjectBlockClick}
                                        width={37}
                                    />
                                )
                            })}

                        </div>
                        
                        {projectImages.slice(1, projectImages.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 2 == 0) {
                                return (
                                    <div className="project-grid-row">
                                        {projectImages.slice(indexOne + 1, indexOne + 3).map((cellImage, indexTwo) => {
                                            return (
                                                <ProjectsBlock 
                                                    projectTitle={projectTitles[indexTwo + indexOne + 1]}
                                                    projectImage={projectImages[indexTwo + indexOne + 1]}
                                                    projectDescription={projectDescriptions[indexTwo + indexOne + 1]}
                                                    onProjectBlockClick={onProjectBlockClick}
                                                    width={37}
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
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={37}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else if (windowWidth > 800 && windowWidth <= 1200) {
            if (projectImages) {
                return (
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={24}/>
                            {projectImages.slice(0, 2).map((cellImage, index) => {
                                return (
                                    <ProjectsBlock 
                                        projectTitle={projectTitles[index]}
                                        projectImage={projectImages[index]}
                                        projectDescription={projectDescriptions[index]}
                                        onProjectBlockClick={onProjectBlockClick}
                                        width={24}
                                    />
                                )
                            })}

                        </div>
                        
                        {projectImages.slice(2, projectImages.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 3 == 0) {
                                return (
                                    <div className="project-grid-row">
                                        {projectImages.slice(indexOne + 2, indexOne + 5).map((cellImage, indexTwo) => {
                                            return (
                                                <ProjectsBlock 
                                                    projectTitle={projectTitles[indexTwo + indexOne + 2]}
                                                    projectImage={projectImages[indexTwo + indexOne + 2]}
                                                    projectDescription={projectDescriptions[indexTwo + indexOne + 2]}
                                                    onProjectBlockClick={onProjectBlockClick}
                                                    width={24}
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
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={24}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else if (windowWidth > 1200 && windowWidth <= 1600) {
            if (projectImages) {
                return (
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={17.5}/>
                            {projectImages.slice(0, 3).map((cellImage, index) => {
                                return (
                                    <ProjectsBlock 
                                        projectTitle={projectTitles[index]}
                                        projectImage={projectImages[index]}
                                        projectDescription={projectDescriptions[index]}
                                        onProjectBlockClick={onProjectBlockClick}
                                        width={17.5}
                                    />
                                )
                            })}

                        </div>
                        
                        {projectImages.slice(3, projectImages.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 4 == 0) {
                                return (
                                    <div className="project-grid-row">
                                        {projectImages.slice(indexOne + 3, indexOne + 7).map((cellImage, indexTwo) => {
                                            return (
                                                <ProjectsBlock 
                                                    projectTitle={projectTitles[indexTwo + indexOne + 3]}
                                                    projectImage={projectImages[indexTwo + indexOne + 3]}
                                                    projectDescription={projectDescriptions[indexTwo + indexOne + 3]}
                                                    onProjectBlockClick={onProjectBlockClick}
                                                    width={17.5}
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
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={17.5}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        } else {
            if (projectImages) {
                return (
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={13.6}/>
                            {projectImages.slice(0, 4).map((cellImage, index) => {
                                return (
                                    <ProjectsBlock 
                                        projectTitle={projectTitles[index]}
                                        projectImage={projectImages[index]}
                                        projectDescription={projectDescriptions[index]}
                                        onProjectBlockClick={onProjectBlockClick}
                                        width={13.6}
                                    />
                                )
                            })}

                        </div>
                        
                        {projectImages.slice(4, projectImages.length).map((cellImageOne, indexOne) => {
                            if (indexOne % 5 == 0) {
                                return (
                                    <div className="project-grid-row">
                                        {projectImages.slice(indexOne + 4, indexOne + 9).map((cellImage, indexTwo) => {
                                            return (
                                                <ProjectsBlock 
                                                    projectTitle={projectTitles[indexTwo + indexOne + 4]}
                                                    projectImage={projectImages[indexTwo + indexOne + 4]}
                                                    projectDescription={projectDescriptions[indexTwo + indexOne + 4]}
                                                    onProjectBlockClick={onProjectBlockClick}
                                                    width={13.6}
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
                    <div className="project-grid-container">
                        <div className='project-grid-row'>
                            <NewProjectButton onNewProjectButtonClicked={onNewProjectButtonClick} width={13.6}/>
                        </div>
                        <div className='bottom-grid-addition'></div>
                    </div>
                )
            } 
        }
    }
}
//         if (projectImages) {
//             return (
//                 <div className="project-grid-container">
//                     <div className='project-grid-row'>
//                         <NewProjectButton onNewProjectButtonClick={onNewProjectButtonClick}/>
//                         {projectImages.slice(0, 2).map((projectImage, index) => {
//                             return (
//                                 <ProjectsBlock 
//                                     projectTitle={projectTitles[index]}
//                                     projectImage={projectImages[index]}
//                                     projectDescription={projectDescriptions[index]}
//                                     onProjectBlockClick={onProjectBlockClick}
//                                 />
//                             )
//                         })}

//                     </div>
                    
//                     {projectImages.slice(2, projectImages.length).map((projectImageOne, indexOne) => {
//                         if (indexOne % 3 == 0) {
//                             return (
//                                 <div className="project-grid-row">
//                                     {projectImages.slice(indexOne + 2, indexOne + 5).map((projectImage, index) => {
//                                         return (
//                                             <ProjectsBlock 
//                                                 projectTitle={projectTitles[index + indexOne + 2]}
//                                                 projectImage={projectImages[index + indexOne + 2]}
//                                                 projectDescription={projectDescriptions[index + indexOne + 2]}
//                                                 onProjectBlockClick={onProjectBlockClick}
//                                             />
//                                         )
//                                     })}
//                                 </div>
//                             )
//                         }
//                     })
                            
//                     }
//                     <div className='bottom-grid-addition'></div>
//                 </div>
//             )
//         } else {
//             return (
//                 <div className="project-grid-container">
//                     <div className='project-grid-row'>
//                         <NewProjectButton onNewProjectButtonClick={onNewProjectButtonClick}/>
//                     </div>
//                     <div className='bottom-grid-addition'></div>
//                 </div>
//             )
//         }
//     }
// }

export default ProjectsGrid