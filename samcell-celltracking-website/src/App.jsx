import logo from './logo.svg';
import './App.css';
import { useState, useEffect, useRef } from 'react'
import ImageAndSegmentationUpload from './components/ImageAndSegmentationUpload';
import CellTrackingPlot from './components/CellTrackingPlot';
import TopBar from './components/TopBar';
import ProjectsGrid from './components/ProjectsGrid';
import ProjectNavigationBar from './components/ProjectNavigationBar';
import CellImageGallery from './components/CellImageGallery';
import SingleImageCellPlot from './components/SingleImageCellPlot';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

function App() {

  document.body.style = 'background: rgb(250, 250, 250)'

  const inputRef = useRef()
  const timeOutId = useRef()

  const [homeSelected, setHomeSelected] = useState(true)
  const [projectsSelected, setProjectsSelected] = useState(false)

  const [singleProjectSelected, setSingleProjectSelected] = useState(false)
  const [selectedProject, setSelectedProject] = useState()

  const [dataOne, setDataOne] = useState()
  const [dataOneValues, setDataOneValues] = useState()
  const [dataOneAllCellsValues, setDataOneAllCellsValues] = useState()

  const [dataTwo, setDataTwo] = useState()
  const [dataTwoValues, setDataTwoValues] = useState()
  const [dataTwoAllCellsValues, setDataTwoAllCellsValues] = useState()

  const [dataThree, setDataThree] = useState()
  const [dataThreeValues, setDataThreeValues] = useState()
  const [dataThreeAllCellsValues, setDataThreeAllCellsValues] = useState()

  const [plotDates, setPlotDates] = useState()

  const [addingNewImage, setAddingNewImage] = useState(false)

  const [onGalleryPage, setOnGalleryPage] = useState(true)

  const [plotAverageCells, setPlotAverageCells] = useState(true)

  const [outliers, setOutliers] = useState()

  const [singleImageMetricTracking, setSingleImageMetricTracking] = useState(false)
  const [singleImageMetricTrackingDate, setSingleImageMetricTrackingDate] = useState()
  const [singleImageMetricOne, setSingleImageMetricOne] = useState()
  const [singleImageMetricOneValues, setSingleImageMetricOneValues] = useState()
  const [singleImageMetricTwo, setSingleImageMetricTwo] = useState()
  const [singleImageMetricTwoValues, setSingleImageMetricTwoValues] = useState()
  const [singleImageMetricThree, setSingleImageMetricThree] = useState()
  const [singleImageMetricThreeValues, setSingleImageMetricThreeValues] = useState()
  const [singleImageMetricFour, setSingleImageMetricFour] = useState()
  const [singleImageMetricFourValues, setSingleImageMetricFourValues] = useState()
  const [singleImageOutliers, setSingleImageOutliers] = useState()

  
  useEffect(() => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Condition', 'Max Variance')

    if (singleProjectSelected) {
      fetch('/get_metrics_with_specific_condition_to_plot', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            const parameterDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parameterDictionary) {
              setPlotDates(parameterDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeValues(parameterDictionary[key].map(obj => obj['Value']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
          
        }
      )

      fetch('/get_metrics_with_specific_condition_to_plot_all_cell_masks', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            setOutliers(data['Outliers'])
            const parametersDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parametersDictionary) {
              setPlotDates(parametersDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
          
        }
      )

      setPlotAverageCells(true)
    }
    
  }, [singleProjectSelected])

  const plotAverageCellsCondition = (condition) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    if (condition != 'Principal Components') {

      formData.append('Condition', condition)

      fetch('/get_metrics_with_specific_condition_to_plot', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            const parameterDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parameterDictionary) {
              setPlotDates(parameterDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeValues(parameterDictionary[key].map(obj => obj['Value']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    } else {
      fetch('/get_pca_metrics_average_cell_masks', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          console.log(data)
          if (data['Success']) {
            const parameterDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parameterDictionary) {
              setPlotDates(parameterDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoValues(parameterDictionary[key].map(obj => obj['Value']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeValues(parameterDictionary[key].map(obj => obj['Value']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    }
    
    setPlotAverageCells(true)
  }

  const plotAllCellsCondition = (condition) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    if (condition != 'Principal Components') {

      formData.append('Condition', condition)

      fetch('/get_metrics_with_specific_condition_to_plot_all_cell_masks', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            setOutliers(data['Outliers'])
            const parametersDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parametersDictionary) {
              setPlotDates(parametersDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    } else {
      fetch('/get_pca_metrics_all_cell_masks', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            setOutliers(data['Outliers'])
            const parametersDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parametersDictionary) {
              setPlotDates(parametersDictionary[key].map(obj => obj['Date']))
              if (i == 1) {
                setDataOne(key)
                setDataOneAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 2) {
                setDataTwo(key)
                setDataTwoAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              } else if (i == 3) {
                setDataThree(key)
                setDataThreeAllCellsValues(parametersDictionary[key].map(obj => obj['Values']))
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    }
    setPlotAverageCells(false)
  }

  const handleNavigationClick = () => {
    if (homeSelected) {
      setProjectsSelected(true)
      setHomeSelected(false)
      setSingleProjectSelected(false)
      setSelectedProject()
      setDataOne()
      setDataOneValues()
      setDataOneAllCellsValues()
      setDataTwo()
      setDataTwoValues()
      setDataTwoAllCellsValues()
      setDataThree()
      setDataThreeValues()
      setDataThreeAllCellsValues()
      setAddingNewImage()
      setPlotDates()
      setOnGalleryPage()
      setPlotAverageCells()
      setOutliers()
      setOnGalleryPage(true)
      setPlotAverageCells(true)
      setSingleImageMetricTracking(false)
    } else {
      setProjectsSelected(false)
      setHomeSelected(true)
      setSingleProjectSelected(false)
      setSelectedProject()
    }
    
  }

  const onProjectBlockClick = (e, projectTitle) => {
    setSingleProjectSelected(true)
    setSelectedProject(projectTitle)
  }

  const onPlotParameterOneSelectionAverage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)

    fetch('/get_specific_metrics_to_plot', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        const parameterDictionary = data['Parameter Dictionary']
        setPlotDates(parameterDictionary[selectedParameter].map(obj => obj['Date']))
        setDataOne(selectedParameter)
        setDataOneValues(parameterDictionary[selectedParameter].map(obj => obj['Value']))
      }
    )
  }

  const onPlotParameterTwoSelectionAverage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)

    fetch('/get_specific_metrics_to_plot', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        const parameterDictionary = data['Parameter Dictionary']
        setPlotDates(parameterDictionary[selectedParameter].map(obj => obj['Date']))
        setDataTwo(selectedParameter)
        setDataTwoValues(parameterDictionary[selectedParameter].map(obj => obj['Value']))
      }
    )
  }

  const onPlotParameterThreeSelectionAverage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)

    fetch('/get_specific_metrics_to_plot', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        const parameterDictionary = data['Parameter Dictionary']
        setPlotDates(parameterDictionary[selectedParameter].map(obj => obj['Date']))
        setDataThree(selectedParameter)
        setDataThreeValues(parameterDictionary[selectedParameter].map(obj => obj['Value']))
      }
    )
  }


  const onPlotParameterOneSelectionAllCells = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', dataTwo)
    formData.append('Other Parameter Two', dataThree)

    fetch('/get_specific_metrics_to_plot_all_cell_masks', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          setOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          setPlotDates(parametersDictionary[selectedParameter].map(obj => obj['Date']))
          setDataOne(selectedParameter)
          setDataOneAllCellsValues(parametersDictionary[selectedParameter].map(obj => obj['Values']))
      }
    )
  }

  const onPlotParameterTwoSelectionAllCells = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', dataOne)
    formData.append('Other Parameter Two', dataThree)

    fetch('/get_specific_metrics_to_plot_all_cell_masks', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        setOutliers(data['Outliers'])
        const parametersDictionary = data['Parameter Dictionary']
        setPlotDates(parametersDictionary[selectedParameter].map(obj => obj['Date']))
        setDataTwo(selectedParameter)
        setDataTwoAllCellsValues(parametersDictionary[selectedParameter].map(obj => obj['Values']))
      }
    )
  }

  const onPlotParameterThreeSelectionAllCells = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', dataOne)
    formData.append('Other Parameter Two', dataTwo)

    fetch('/get_specific_metrics_to_plot_all_cell_masks', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        setOutliers(data['Outliers'])
        const parametersDictionary = data['Parameter Dictionary']
        setPlotDates(parametersDictionary[selectedParameter].map(obj => obj['Date']))
        setDataThree(selectedParameter)
        setDataThreeAllCellsValues(parametersDictionary[selectedParameter].map(obj => obj['Values']))
      }
    )
  }



  const onAddImageClick = () => {
    setAddingNewImage(true)
  }

  const onProjectPageSelected = (page) => {
    setSingleImageMetricTracking(false)
    setSingleImageMetricOne()
    setSingleImageMetricOneValues()
    setSingleImageMetricTwo()
    setSingleImageMetricTwoValues()
    setSingleImageMetricThree()
    setSingleImageMetricThreeValues()
    setSingleImageMetricFour()
    setSingleImageMetricFourValues()
    if (page == 'Image Gallery') {
      setOnGalleryPage(true)
    } else {
      plotAverageCellsCondition('Max Variance')
      setOnGalleryPage(false)
    }
  }

  const onImageGalleryBlockClick = (date) => {
    console.log(date + " Clicked!")

    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Condition', "Max Variance")
    formData.append('Date', date)

    fetch('/get_metrics_with_specific_condition_to_plot_all_cell_masks_single_image', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
      data => {
        if (data['Success']) {
          setSingleImageOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          var i = 1
          for (const key in parametersDictionary) {
            if (i == 1) {
              setSingleImageMetricOne(key)
              setSingleImageMetricOneValues(parametersDictionary[key])
            } else if (i == 2) {
              setSingleImageMetricTwo(key)
              setSingleImageMetricTwoValues(parametersDictionary[key])
            } else if (i == 3) {
              setSingleImageMetricThree(key)
              setSingleImageMetricThreeValues(parametersDictionary[key])
            } else if (i == 4) {
              setSingleImageMetricFour(key)
              setSingleImageMetricFourValues(parametersDictionary[key])
            }
            i += 1
          }
        } else {
          console.log('FAILURE')
        }
      }
    )
    timeOutId.current = setTimeout(() => {
      setSingleImageMetricTrackingDate(date)
      setSingleImageMetricTracking(true)
    }, 200)
    //clearTimeout(timeOutId.current)
    
  }

  const onPlotAllCellsConditionSingleImage = (condition) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Date', singleImageMetricTrackingDate)
    if (condition != 'Principal Components') {
      formData.append('Condition', condition)

      fetch('/get_metrics_with_specific_condition_to_plot_all_cell_masks_single_image', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            setSingleImageOutliers(data['Outliers'])
            const parametersDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parametersDictionary) {
              if (i == 1) {
                setSingleImageMetricOne(key)
                setSingleImageMetricOneValues(parametersDictionary[key])
              } else if (i == 2) {
                setSingleImageMetricTwo(key)
                setSingleImageMetricTwoValues(parametersDictionary[key])
              } else if (i == 3) {
                setSingleImageMetricThree(key)
                setSingleImageMetricThreeValues(parametersDictionary[key])
              } else if (i == 4) {
                setSingleImageMetricFour(key)
                setSingleImageMetricFourValues(parametersDictionary[key])
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    } else {
      formData.append('Condition', condition)

      fetch('/get_pca_metrics_all_cell_masks_single_image', {
        method: 'POST',
        body: formData
      }).then(
        res => res.json()
      ).then(
        data => {
          if (data['Success']) {
            setSingleImageOutliers(data['Outliers'])
            const parametersDictionary = data['Parameter Dictionary']
            var i = 1
            for (const key in parametersDictionary) {
              if (i == 1) {
                setSingleImageMetricOne(key)
                setSingleImageMetricOneValues(parametersDictionary[key])
              } else if (i == 2) {
                setSingleImageMetricTwo(key)
                setSingleImageMetricTwoValues(parametersDictionary[key])
              } else if (i == 3) {
                setSingleImageMetricThree(key)
                setSingleImageMetricThreeValues(parametersDictionary[key])
              } else if (i == 4) {
                setSingleImageMetricFour(key)
                setSingleImageMetricFourValues(parametersDictionary[key])
              }
              i += 1
            }
          } else {
            console.log('FAILURE')
          }
        }
      )
    }

    
    
  }


  const onPlotParameterOneSelectionSingleImage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Date', singleImageMetricTrackingDate)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', singleImageMetricTwo)
    formData.append('Other Parameter Two', singleImageMetricThree)
    formData.append('Other Parameter Three', singleImageMetricFour)

    fetch('/get_specific_metrics_to_plot_single_image', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          setOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          setSingleImageMetricOne(selectedParameter)
          setSingleImageMetricOneValues(parametersDictionary[selectedParameter])
      }
    )
  }

  const onPlotParameterTwoSelectionSingleImage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Date', singleImageMetricTrackingDate)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', singleImageMetricOne)
    formData.append('Other Parameter Two', singleImageMetricThree)
    formData.append('Other Parameter Three', singleImageMetricFour)

    fetch('/get_specific_metrics_to_plot_single_image', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          setOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          setSingleImageMetricTwo(selectedParameter)
          setSingleImageMetricTwoValues(parametersDictionary[selectedParameter])
      }
    )
  }

  const onPlotParameterThreeSelectionSingleImage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Date', singleImageMetricTrackingDate)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', singleImageMetricOne)
    formData.append('Other Parameter Two', singleImageMetricTwo)
    formData.append('Other Parameter Three', singleImageMetricFour)

    fetch('/get_specific_metrics_to_plot_single_image', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          setOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          setSingleImageMetricThree(selectedParameter)
          setSingleImageMetricThreeValues(parametersDictionary[selectedParameter])
      }
    )
  }

  const onPlotParameterFourSelectionSingleImage = (selectedParameter) => {
    const formData = new FormData()
    formData.append('Project', selectedProject)
    formData.append('Date', singleImageMetricTrackingDate)
    formData.append('Parameter', selectedParameter)
    formData.append('Other Parameter One', singleImageMetricOne)
    formData.append('Other Parameter Two', singleImageMetricTwo)
    formData.append('Other Parameter Three', singleImageMetricThree)

    fetch('/get_specific_metrics_to_plot_single_image', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          setOutliers(data['Outliers'])
          const parametersDictionary = data['Parameter Dictionary']
          setSingleImageMetricFour(selectedParameter)
          setSingleImageMetricFourValues(parametersDictionary[selectedParameter])
      }
    )
  }


  const onExportClicked = () => {
    const formData = new FormData()
    formData.append('Project', selectedProject)

    fetch('/get_project_data_to_export', {
      method: 'POST',
      body: formData
    }).then(
      res => res.json()
    ).then(
        data => {
          const projectExportData = data['Data']
          const worksheet = XLSX.utils.json_to_sheet(projectExportData);
          const workbook = XLSX.utils.book_new();
          XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
          
          // Buffer to store the generated Excel file
          const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
          const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8' });
          
          saveAs(blob, selectedProject + " Metric Tracking.xlsx");
      }
    )


    
  }



  if (homeSelected) {
    return (
      <TopBar handleNavigationClick={handleNavigationClick} topBarText={'SAMCell'} buttonText={'Projects'}/>
      
    )
  } else if (projectsSelected) {
    if (singleProjectSelected) {
      if (!onGalleryPage) {
        return (
          <div className="App">
            <TopBar handleNavigationClick={handleNavigationClick} topBarText={selectedProject} buttonText={'Home'}/>
            <ProjectNavigationBar onPageSelection={onProjectPageSelected}/>
            <CellTrackingPlot 
              project={selectedProject}
              dataOne={dataOne}
              dataOneValues={dataOneValues}
              dataOneAllCellsValues={dataOneAllCellsValues}
              dataTwo={dataTwo}
              dataTwoValues={dataTwoValues}
              dataTwoAllCellsValues={dataTwoAllCellsValues}
              dataThree={dataThree}
              dataThreeValues={dataThreeValues}
              dataThreeAllCellsValues={dataThreeAllCellsValues}
              dates={plotDates}
              onSelectionOneMadeAverage={onPlotParameterOneSelectionAverage}
              onSelectionTwoMadeAverage={onPlotParameterTwoSelectionAverage}
              onSelectionThreeMadeAverage={onPlotParameterThreeSelectionAverage}
              onSelectionOneMadeAllCells={onPlotParameterOneSelectionAllCells}
              onSelectionTwoMadeAllCells={onPlotParameterTwoSelectionAllCells}
              onSelectionThreeMadeAllCells={onPlotParameterThreeSelectionAllCells}
              plotAllCells={plotAllCellsCondition}
              plotAverageCells={plotAverageCellsCondition}
              allDataOutlierIndices={outliers}
              onExportClicked={onExportClicked}
            />
          </div>
        );
        
      } else {
        if (singleImageMetricTracking) {
          return (
            <div className="App">
              <TopBar handleNavigationClick={handleNavigationClick} topBarText={selectedProject} buttonText={'Home'}/>
              <ProjectNavigationBar onPageSelection={onProjectPageSelected}/>
              <SingleImageCellPlot 
                project={selectedProject}
                date={singleImageMetricTrackingDate}
                dataOne={singleImageMetricOne}
                dataOneAllCellsValues={singleImageMetricOneValues}
                dataTwo={singleImageMetricTwo}
                dataTwoAllCellsValues={singleImageMetricTwoValues}
                dataThree={singleImageMetricThree}
                dataThreeAllCellsValues={singleImageMetricThreeValues}
                dataFour={singleImageMetricFour}
                dataFourAllCellsValues={singleImageMetricFourValues}
                onSelectionOneMadeAllCells={onPlotParameterOneSelectionSingleImage}
                onSelectionTwoMadeAllCells={onPlotParameterTwoSelectionSingleImage}
                onSelectionThreeMadeAllCells={onPlotParameterThreeSelectionSingleImage}
                onSelectionFourMadeAllCells={onPlotParameterFourSelectionSingleImage}
                plotAllCells={onPlotAllCellsConditionSingleImage}
                allDataOutlierIndices={singleImageOutliers}
              />
            </div>
          );
        } else {
          return (
            <div className="App">
              <TopBar handleNavigationClick={handleNavigationClick} topBarText={selectedProject} buttonText={'Home'}/>
              <ProjectNavigationBar onPageSelection={onProjectPageSelected}/>
              <CellImageGallery project={selectedProject} dates={plotDates} onImageGalleryBlockClick={(date) => onImageGalleryBlockClick(date)}/>
            </div>
          );
        }
        
      }
      
    } else {
      return (
        <div className="App">
          <TopBar handleNavigationClick={handleNavigationClick} topBarText={'SAMCell - Projects'} buttonText={'Home'}/>
          <ProjectsGrid onProjectBlockClick={onProjectBlockClick}/>
        </div>
      );
    }
    
    }
    
  
}

export default App;
