import React, { useState, useEffect, useRef } from 'react'
import Plot from 'react-plotly.js'
import DropDownMenu from './DropDownMenu'
import BlankImage from '../BlankImage.png'
import SampleImageReplacement from '../SampleImageReplacement.png'
import AverageOrAllCellsSelection from './AverageOrAllCellsSelection'

/**
 * CellTrackingPlot Component that displays a plot of the metrics for the project (single, all cells, or average)
 *
 * @param {string} project - Title of the project
 * @param {string} dataOne - Name of the first parameter
 * @param {list} dataOneValues - list of average parameterOne values for each image
 * @param {list} dataOneAllCellsValues - list of parameterOne values for each segmentation in each image
 * @param {string} dataTwo - Name of the second parameter
 * @param {list} dataTwoValues - list of average parameterTwo values for each image
 * @param {list} dataTwoAllCellsValues - list of parameterTwo values for each segmentation in each image
 * @param {string} dataThree - Name of the third parameter
 * @param {list} dataThreeValues - list of average parameterThree values for each image
 * @param {list} dataThreeAllCellsValues - list of parameterThree values for each segmentation in each image
 * @param {list} dates - List of dates of when the images were taken
 * @param {func} onSelectionOneMadeAverage - Function that is called when a new metric is selected to be the first parameter on the average plot
 * @param {func} onSelectionTwoMadeAverage - Function that is called when a new metric is selected to be the second parameter on the average plot
 * @param {func} onSelectionThreeMadeAverage - Function that is called when a new metric is selected to be the three parameter on the average plot
 * @returns {React.JSX.Element} - The CellTrackingPlot element.
 */
function CellTrackingPlot({ project, dataOne, dataOneValues, dataOneAllCellsValues, dataTwo, dataTwoValues, dataTwoAllCellsValues, dataThree, dataThreeValues, dataThreeAllCellsValues, dates, onSelectionOneMadeAverage, onSelectionTwoMadeAverage, onSelectionThreeMadeAverage, onSelectionOneMadeAllCells, onSelectionTwoMadeAllCells, onSelectionThreeMadeAllCells, plotAverageCells, plotAllCells, allDataOutlierIndices, onExportClicked }) {

    const plotRef = useRef()
    const timeOutId = useRef()

    const [text, setText] = useState([])
    const [allCellsDisplayText, setAllCellsDisplayText] = useState([])
    const [colors, setColors] = useState([])
    const [intensityRange, setIntensityRange] = useState([])

    const [dataOneAllCellsValuesLocal, setDataOneAllCellsValuesLocal] = useState(dataOneAllCellsValues)
    const [dataTwoAllCellsValuesLocal, setDataTwoAllCellsValuesLocal] = useState(dataTwoAllCellsValues)
    const [dataThreeAllCellsValuesLocal, setDataThreeAllCellsValuesLocal] = useState(dataThreeAllCellsValues)


    const [pointFocused, setPointFocused] = useState(false)
    const [focusedColors, setFocusedColors] = useState([])
    const [focusedDate, setFocusedDate] = useState()
    const [focusedDateMargin, setFocusedDateMargin] = useState('')

    const [display, setDisplay] = useState(true)

    const [currentCamera, setCurrentCamera] = useState({
        up: {x: 0, y: 0, z: 1},
        center: {x:0, y:0, z:0},
        eye: {x:1.25, y:1.25, z:1.25}
    })
    const [tempCamera, setTempCamera] = useState()

    const [sampleImage, setSampleImage] = useState(SampleImageReplacement)
    const [sampleCellImage, setSampleCellImage] = useState(SampleImageReplacement)

    const [averageCellsSelected, setAverageCellsSelected] = useState(true)

    const [hideOutliersChecked, setHideOutliersChecked] = useState(false)

    const [lastSegmentationIndex, setLastSegmentationIndex] = useState(0)



    window.addEventListener('resize', () => onWindowUpdate())

    useEffect(() => {
        if (dataOne) {
            const formData = new FormData()
            formData.append('Project', project)
            formData.append('Date', dates[0])

            fetch('/get_specific_image', {method: 'POST', body: formData}).then(
                res => res.blob()
            ).then(
                blob => {
                    setSampleImage(URL.createObjectURL(blob))
                }
            )
        }
    }, [])

    useEffect(() => {
        setDataOneAllCellsValuesLocal(dataOneAllCellsValues)
        setDataTwoAllCellsValuesLocal(dataTwoAllCellsValues)
        setDataThreeAllCellsValuesLocal(dataThreeAllCellsValues)
    }, [dataOneAllCellsValues, dataTwoAllCellsValues, dataThreeAllCellsValues])

    useEffect(() => {
        const tempIntensityRange = []
        for (var i = 0; i < 256; i++) {
            tempIntensityRange[i] = i
        }
        setIntensityRange(tempIntensityRange)
    }, [])

    useEffect(() => {
        if (dataOne) {
            const tempText = []
            for (var i = 0; i < dates.length; i++) {
                tempText[i] = [dates[i], dataOne, dataTwo, dataThree]
            }

            setText(tempText)
        }
    }, [dataOne, dataTwo, dataThree])

    useEffect(() => {
        if (dataOne) {
            const colorsTemp = []
            colorsTemp[0] = 'rgb(255, 0, 0)'

            var totalDateSum = 0;
            for (var i = 1; i < dates.length; i++) {
                totalDateSum += Date.parse(dates[i])
            }

            var dateRange = Date.parse(dates[dates.length - 1]) - Date.parse(dates[0]);
            for (var i = 1; i < dates.length; i++) {
                const ratio = (Date.parse(dates[i]) - Date.parse(dates[0])) / dateRange
                const blue = Math.round(255 * ratio)
                const red = Math.round(255 - (255 * ratio))
                colorsTemp[i] = `rgb(${red}, 0, ${blue})`;
            }

            setColors(colorsTemp)
        }
    }, [])

    const onWindowUpdate = () => {
        setDisplay(false)
    }

    const get_closest_color = (divBlueValue) => {

        var closestIndex = 0;
        var leastBlueDiff = 256;
        for (var i = 0; i < colors.length; i++) {
            const blue = colors[i].slice(colors[i].lastIndexOf(',') + 2, colors[i].indexOf(')'))
            const blueDiff = Math.abs(blue - divBlueValue)
            if (blueDiff < leastBlueDiff) {
                closestIndex = i
                leastBlueDiff = blueDiff
            }
        }
        
        const tempFocusedColors = []
        for (var i = 0; i < colors.length; i++) {
            if (i == closestIndex) {
                var tempColor = 'rgba' + colors[i].slice(colors[i].indexOf('('), colors[i].indexOf(')')) + ', 1)'
                tempFocusedColors[i] = tempColor
            } else {
                var tempColor = 'rgba' + colors[i].slice(colors[i].indexOf('('), colors[i].indexOf(')')) + ', 0)'
                tempFocusedColors[i] = tempColor
            }
        }

        const margin = `min(${1 + (divBlueValue * 0.1568627)}vw, ${28 + (divBlueValue * 2.5098)}px)`


        if (dates[closestIndex] != focusedDate) {
            const formData = new FormData()
            formData.append('Project', project)
            formData.append('Date', dates[closestIndex])

            fetch('/get_specific_image', {method: 'POST', body: formData}).then(
                res => res.blob()
            ).then(
                blob => {
                    setSampleImage(URL.createObjectURL(blob))
                }
            )
            setSampleCellImage(SampleImageReplacement)
        }
        


        setFocusedColors(tempFocusedColors)
        setFocusedDate(dates[closestIndex])
        setFocusedDateMargin(margin)
        setPointFocused(true)

    }

    const onMouseLeaveColorFrequency = () => {
        setPointFocused(false)
    }

    const handleLayoutChange = (e) => {
        setTempCamera(e['scene.camera'])
    }

    const onAverageClick = () => {
        if (!averageCellsSelected)  {
            const formData = new FormData()
            formData.append('Project', project)
            formData.append('Date', dates[0])

            fetch('/get_specific_image', {method: 'POST', body: formData}).then(
                res => res.blob()
            ).then(
                blob => {
                    setSampleImage(URL.createObjectURL(blob))
                }
            )

            setAverageCellsSelected(true)
            plotAverageCells("Max Variance")
            setHideOutliersChecked(false)
        }
    }

    const onAllCellsClick = () => {
        setAverageCellsSelected(false)
        if (averageCellsSelected) {

            const formData = new FormData()
            formData.append('Project', project)
            formData.append('Date', dates[0])

            fetch('/get_specific_image', {method: 'POST', body: formData}).then(
                res => res.blob()
            ).then(
                blob => {
                    setSampleImage(URL.createObjectURL(blob))
                }
            )

            setSampleCellImage(SampleImageReplacement)
            plotAllCells("Max Variance")
            setHideOutliersChecked(false)
        }
    }

    const selectionOneMadeAverage = (parameter) => {
        onSelectionOneMadeAverage(parameter)
    }

    const selectionTwoMadeAverage = (parameter) => {
        onSelectionTwoMadeAverage(parameter)
    }

    const selectionThreeMadeAverage = (parameter) => {
        onSelectionThreeMadeAverage(parameter)
    }

    const selectionOneMadeAllCells = (parameter) => {
        onSelectionOneMadeAllCells(parameter)
    }

    const selectionTwoMadeAllCells = (parameter) => {
        onSelectionTwoMadeAllCells(parameter)
    }

    const selectionThreeMadeAllCells = (parameter) => {
        onSelectionThreeMadeAllCells(parameter)
    }

    const handleOnHideOutliersClicked = () => {
        if (hideOutliersChecked) {
            setHideOutliersChecked(false)
        } else {
            setHideOutliersChecked(true)
        }
    }

    useEffect(() => {
        if (hideOutliersChecked) {
            var tempDataOneAllCellValuesLocal = []
            var tempDataTwoAllCellValuesLocal = []
            var tempDataThreeAllCellValuesLocal = []

            for (var i = 0; i < dataOneAllCellsValues.length; i++) {
                tempDataOneAllCellValuesLocal[i] = dataOneAllCellsValues[i].filter((value, index) => !allDataOutlierIndices[i].includes(index))
                tempDataTwoAllCellValuesLocal[i] = dataTwoAllCellsValues[i].filter((value, index) => !allDataOutlierIndices[i].includes(index))
                tempDataThreeAllCellValuesLocal[i] = dataThreeAllCellsValues[i].filter((value, index) => !allDataOutlierIndices[i].includes(index))
            }
            setDataOneAllCellsValuesLocal(tempDataOneAllCellValuesLocal)
            setDataTwoAllCellsValuesLocal(tempDataTwoAllCellValuesLocal)
            setDataThreeAllCellsValuesLocal(tempDataThreeAllCellValuesLocal)

        } else {
            setDataOneAllCellsValuesLocal(dataOneAllCellsValues)
            setDataTwoAllCellsValuesLocal(dataTwoAllCellsValues)
            setDataThreeAllCellsValuesLocal(dataThreeAllCellsValues)
        }
    }, [hideOutliersChecked, dataOne, dataTwo, dataThree, averageCellsSelected])

    const onDatapointHover = (e) => {
        if (e.points[0].text[4] != lastSegmentationIndex) {
            setLastSegmentationIndex(e.points[0].text[4])
            clearTimeout(timeOutId.current)
            timeOutId.current = setTimeout(() => {
                const point_text = e.points[0].text
                console.log(point_text)

                setFocusedDate(point_text[0])

                var formData = new FormData()
                formData.append('Project', project)
                formData.append('Date', point_text[0])
                formData.append('Segmentation Index', point_text[4])

                fetch('/get_whole_image_with_highlighted_segmentation', {
                    method: "POST",
                    body: formData
                }).then(
                    res => res.blob()
                ).then(
                    blob => {
                        setSampleImage(URL.createObjectURL(blob))
                    }
                )

                fetch('/get_segmented_cell_image', {
                    method: "POST",
                    body: formData
                }).then(
                    res => res.blob()
                ).then(
                    blob => {
                        setSampleCellImage(URL.createObjectURL(blob))
                    }
                )
            }, 100)
        }
        
    }

    useEffect(() => {
        var tempText = []
        for (var i = 0; i < dataOneAllCellsValues.length; i++) {
            tempText[i] = []
            for (var j = 0; j < dataOneAllCellsValues[i].length; j++) {
                tempText[i][j] = [dates[i], dataOne, dataTwo, dataThree, j]
            }
        }
        setAllCellsDisplayText(tempText)
        
    }, [dataOne, dataTwo, dataThree])


    if (dataOne) {
        if (display) {
            if(averageCellsSelected) {
                return (
                    <div>
                        <AverageOrAllCellsSelection onAllCellsClick={onAllCellsClick} onAverageClick={onAverageClick} selectedButton={'Average'}/>
                        <div style={{justifyContent: 'center', justifySelf: 'center', marginBottom: '10vw', marginTop: 'min(3vw, 30px)', display: 'flex'}}>
                            <div style={{width: 'min(15vw, 200px)', backgroundColor: 'rgb(230, 230, 230)'}}>
                                <div style={{height: 'min(40vw, 685px)', textAlign: 'center'}}>
                                    <div style={{fontSize: "min(1.5vw, 20px)", marginTop: 'min(2vw, 20px)'}}>Plot Options:</div>
                                    <button 
                                        onClick={() => plotAverageCells('Max Variance')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)',
                                            marginBottom: 'min(0.5vw, 2px)'
                                        }}
                                    >Max Variance</button>
                                    <button 
                                        onClick={() => plotAverageCells('Min Variance')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)',
                                            marginBottom: 'min(0.5vw, 2px)'
                                        }}
                                    >Min Variance</button>
                                    <button 
                                        onClick={() => plotAverageCells('Max Range')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Max Range</button>
                                    <button 
                                        onClick={() => plotAverageCells('Min Range')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Min Range</button>
                                    <button 
                                        onClick={() => plotAverageCells('Max Time Correlation')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Max Time Correlation</button>
                                    <button 
                                        onClick={() => plotAverageCells('Min Time Correlation')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Min Time Correlation</button>
                                    <button 
                                        onClick={() => plotAverageCells('Principal Components')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Principal Components</button>
                                </div>
                                <div style={{textAlign: 'center'}}>
                                    <img 
                                        src={sampleImage} 
                                        alt={""}
                                        style={{
                                            width: "90%",
                                            height: "min(10vw, 133px)",
                                        }}
                                    />
                                    <div style={{fontSize: "min(0.9vw, 10px)"}}>{focusedDate}</div>
                                </div>
                                
                            </div>
                            <div>
                                <Plot 
                                    data={
                                        [
                                            {
                                                x: dataOneValues,
                                                y: dataTwoValues,
                                                z: dataThreeValues,
                                                text: text,
                                                hovertemplate: 
                                                    '<br><u><b>%{text[0]}</b></u><br>' +
                                                    '<b>%{text[1]}</b>: %{x:.2f}' +
                                                    '<br><b>%{text[2]}</b>: %{y:.2f}<br>' +
                                                    '<b>%{text[3]}</b>: %{z:.2f}',
                                                type: 'scatter3d',
                                                mode: 'markers',
                                                marker: {
                                                    size: 6,
                                                    color: (pointFocused) ? focusedColors : colors,
                                                    opacity: 1
                                                },
                                                showlegend: false,
                                                name: ""
                                                
                                            },
                                        ]
                                    }
                                    layout={{
                                        title: { text: 'Cell Tracking Plot' },
                                        scene: {
                                            xaxis: { title: dataOne + ' (X)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            yaxis: { title: dataTwo + ' (Y)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            zaxis: { title: dataThree + '(Z)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            camera: currentCamera,
                                        },
                                        margin: {
                                            l: 50,
                                            r: 50,
                                            t: 70,
                                            b: 30,
                                        },
                                        colorway: ['#1f77b4', '#ff7f0e'],
                                        uirevision: 'true'
                                    }}
                                    style={{
                                        width: 'min(50vw, 800px)',
                                        height: 'min(45vw, 750px)'
                                    }}
                                    onRelayout={(e) => handleLayoutChange(e)}
                                    onClick={(e) => handleLayoutChange(e)}
                                    onAfterPlot={() => setCurrentCamera(tempCamera)}
                                />
                                <div style={{width: 'min(50vw, 800px)', height: 'min(6vw, 80px)', backgroundColor: 'white'}}>
                                    <div style={{fontSize: 'min(0.9vw, 10px)', marginLeft: focusedDateMargin, color: pointFocused ? 'black' : 'white'}}>{focusedDate}</div>
                                    <div style={{display: 'flex', marginLeft: 'min(5vw, 80px)', backgroundColor: 'black', height: 'min(2vw, 25px)', width: 'min(40vw, 640px)'}}>
                                        {intensityRange.map((num, index) => {
                                            return (
                                                <div onMouseEnter={() => get_closest_color(num)} onMouseLeave={() => onMouseLeaveColorFrequency()} style={{width: "min(0.1568627vw, 2.5098px)", height: "min(2vw, 25px)", backgroundColor: `rgb(${255 - num}, 0, ${num})`}}/>
                                            )
                                        })}
                                    </div>
                                    <div style={{display: 'flex', marginLeft: '1vw', width: '50vw', marginTop: '0.5vw'}}>
                                        <div style={{fontSize: 'min(1vw, 14px)'}}>{dates[0]}</div>
                                        <div style={{fontSize: 'min(1vw, 14px)', marginLeft: 'min(29vw, 510px)'}}>{dates[dates.length - 1]}</div>
                                    </div>
                                </div>
                                <DropDownMenu 
                                    numParameters={3}
                                    onSelectionOneMade={selectionOneMadeAverage}
                                    onSelectionTwoMade={selectionTwoMadeAverage}
                                    onSelectionThreeMade={selectionThreeMadeAverage}
                                    parameterOne={dataOne}
                                    parameterTwo={dataTwo}
                                    parameterThree={dataThree}
                                />
                            </div>
                            
                        </div>
                    </div>
                )
            } else {
                return (
                    <div>
                        <button style={{
                                marginTop: 'min(2vw, 20px)',
                                marginLeft: 'min(2vw, 20px)',
                                backgroundColor: 'rgb(63, 63, 163)',
                                color: 'rgb(230, 230, 230)',
                                fontSize: 'min(2.5vw, 18px)',
                                fontWeight: '600',
                                paddingLeft: 'min(1.5vw, 15px)',
                                paddingRight: 'min(1.5vw, 15px)',
                                paddingTop: '10px',
                                paddingBottom: '10px',
                                borderRadius: '14px',
                                borderColor: 'rgb(13, 13, 83)',
                                borderWidth: '1.8px',
                                borderStyle: 'solid',
                            }}
                            onClick={() => onExportClicked()}
                        >Export</button>
                        <AverageOrAllCellsSelection onAllCellsClick={onAllCellsClick} onAverageClick={onAverageClick} selectedButton={'All Cells'}/>
                        <div style={{justifyContent: 'center', justifySelf: 'center', marginBottom: '10vw', marginTop: 'min(3vw, 30px)', display: 'flex'}}>
                            <div style={{width: 'min(15vw, 200px)', backgroundColor: 'rgb(230, 230, 230)'}}>
                                <div style={{height: 'min(33vw, 610px)', textAlign: 'center'}}>
                                    <div style={{fontSize: "min(1.5vw, 20px)", marginTop: 'min(2vw, 20px)'}}>Plot Options:</div>
                                    <button 
                                        onClick={() => plotAllCells('Max Variance')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)',
                                            marginBottom: 'min(0.5vw, 2px)'
                                        }}
                                    >Max Variance</button>
                                    <button 
                                        onClick={() => plotAllCells('Min Variance')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)',
                                            marginBottom: 'min(0.5vw, 2px)'
                                        }}
                                    >Min Variance</button>
                                    <button 
                                        onClick={() => plotAllCells('Max Range')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Max Range</button>
                                    <button 
                                        onClick={() => plotAllCells('Min Range')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Min Range</button>
                                    <button 
                                        onClick={() => plotAllCells('Max Time Correlation')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Max Time Correlation</button>
                                    <button 
                                        onClick={() => plotAllCells('Min Time Correlation')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Min Time Correlation</button>
                                    <button 
                                        onClick={() => plotAllCells('Principal Components')}
                                        style={{
                                            width: '90%',
                                            height: 'fit-content',
                                            padding: 'min(0.5vw, 5px)',
                                            fontSize: 'min(1.2vw, 15px)'
                                        }}
                                    >Principal Components</button>
                                    <div style={{display: 'flex', justifyContent: 'center', marginTop: 'min(0.5vw, 5px)'}}>
                                        <div style={{fontSize: 'min(1.6vw, 15px)', fontWeight: '500'}}>Hide Outliers: </div>
                                        <input 
                                            type='checkbox'
                                            checked={hideOutliersChecked}
                                            onChange={() => handleOnHideOutliersClicked()}
                                        />
                                    </div>
                                    
                                </div>
                                <div style={{textAlign: 'center'}}>
                                    <img 
                                        src={sampleCellImage} 
                                        alt={""}
                                        style={{
                                            maxWidth: "90%",
                                            minWidth: "11%",
                                            height: "min(6vw, 80px)",
                                        }}
                                    />
                                    <img 
                                        src={sampleImage} 
                                        alt={""}
                                        style={{
                                            width: "90%",
                                            height: "min(10vw, 133px)",
                                        }}
                                    />
                                    <div style={{fontSize: "min(0.9vw, 10px)"}}>{focusedDate}</div>
                                </div>
                                
                            </div>
                            <div>
                                <Plot 
                                    data={
                                        dataOneAllCellsValues.map((values, index) => {
                                            return (
                                                {
                                                    x: dataOneAllCellsValuesLocal[index],
                                                    y: dataTwoAllCellsValuesLocal[index],
                                                    z: dataThreeAllCellsValuesLocal[index],
                                                    //text: Array(dataOneAllCellsValues[index].length).fill(text[index]),
                                                    text: allCellsDisplayText[index],
                                                    hovertemplate: 
                                                        '<br><u><b>%{text[0]}</b></u><br>' +
                                                        '<b>%{text[1]}</b>: %{x:.2f}' +
                                                        '<br><b>%{text[2]}</b>: %{y:.2f}<br>' +
                                                        '<b>%{text[3]}</b>: %{z:.2f}',
                                                    type: 'scatter3d',
                                                    mode: 'markers',
                                                    marker: {
                                                        size: 1.5,
                                                        color: (pointFocused) ? focusedColors[index] : colors[index],
                                                        opacity: 1
                                                    },
                                                    showlegend: false,
                                                    name: ""
                                                }
                                            )   
                                        }) 
                                    }
                                    layout={{
                                        title: { text: 'Cell Tracking Plot' },
                                        scene: {
                                            xaxis: { title: dataOne + ' (X)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            yaxis: { title: dataTwo + ' (Y)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            zaxis: { title: dataThree + '(Z)', titlefont: {size: 10}, tickfont: {size: 10} },
                                            camera: currentCamera,
                                        },
                                        margin: {
                                            l: 50,
                                            r: 50,
                                            t: 70,
                                            b: 30,
                                        },
                                        colorway: ['#1f77b4', '#ff7f0e'],
                                        uirevision: 'true'
                                    }}
                                    style={{
                                        width: 'min(50vw, 800px)',
                                        height: 'min(45vw, 750px)',
                                    }}
                                    onRelayout={(e) => handleLayoutChange(e)}
                                    onClick={(e) => handleLayoutChange(e)}
                                    onAfterPlot={() => setCurrentCamera(tempCamera)}
                                    onHover={(e) => onDatapointHover(e)}
                                />
                                <div style={{width: 'min(50vw, 800px)', height: 'min(6vw, 80px)', backgroundColor: 'white'}}>
                                    <div style={{fontSize: 'min(0.9vw, 10px)', marginLeft: focusedDateMargin, color: pointFocused ? 'black' : 'white'}}>{focusedDate}</div>
                                    <div style={{display: 'flex', marginLeft: 'min(5vw, 80px)', backgroundColor: 'black', height: 'min(2vw, 25px)', width: 'min(40vw, 640px)'}}>
                                        {intensityRange.map((num, index) => {
                                            return (
                                                <div onMouseEnter={() => get_closest_color(num)} onMouseLeave={() => onMouseLeaveColorFrequency()} style={{width: "min(0.1568627vw, 2.5098px)", height: "min(2vw, 25px)", backgroundColor: `rgb(${255 - num}, 0, ${num})`}}/>
                                            )
                                        })}
                                    </div>
                                    <div style={{display: 'flex', marginLeft: '1vw', width: '50vw', marginTop: '0.5vw'}}>
                                        <div style={{fontSize: 'min(1vw, 14px)'}}>{dates[0]}</div>
                                        <div style={{fontSize: 'min(1vw, 14px)', marginLeft: 'min(29vw, 510px)'}}>{dates[dates.length - 1]}</div>
                                    </div>
                                </div>
                                <DropDownMenu 
                                    numParameters={3}
                                    onSelectionOneMade={selectionOneMadeAllCells}
                                    onSelectionTwoMade={selectionTwoMadeAllCells}
                                    onSelectionThreeMade={selectionThreeMadeAllCells}
                                    parameterOne={dataOne}
                                    parameterTwo={dataTwo}
                                    parameterThree={dataThree}
                                />
                            </div>
                            
                        </div>
                    </div>
                )
            }
            
        } else {
            return (
                <div style={{justifySelf: 'center', marginTop: '35vh'}}>
                    <button 
                    onClick={() => setDisplay(true)}
                    style={{
                    fontSize: "min(2vw, 25px)",
                    color: 'rgb(250, 250, 250)',
                    backgroundColor: 'rgb(50, 250, 50)',
                    paddingLeft: 'min(2vw, 20px)',
                    paddingRight: 'min(2vw, 20px)',
                    paddingTop: 'min(1vw, 10px)',
                    paddingBottom: 'min(1vw, 10px)',
                    borderWidth: 'min(0.25vw, 2px)',
                    borderRadius: 'min(2vw, 12px)',
                    justifySelf: 'center'
                    }}
                >Press to Reload</button>
                </div>
            )
        }
    } else {
        return (
            <div style={{textAlign: 'center', fontSize: 'min(5vw, 30px)', marginTop: '40vh'}}>Add Images to Analyze Metrics</div>
        )
    }
    
        
}

export default CellTrackingPlot