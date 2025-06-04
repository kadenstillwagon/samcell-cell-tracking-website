import React, { useState, useEffect, useRef } from 'react'
import Plot from 'react-plotly.js'
import DropDownMenu from './DropDownMenu'
import SampleImageReplacement from '../SampleImageReplacement.png'

function SingleImageCellPlot({ project, date, dataOne, dataOneAllCellsValues, dataTwo, dataTwoAllCellsValues, dataThree, dataThreeAllCellsValues, dataFour, dataFourAllCellsValues, onSelectionOneMadeAllCells, onSelectionTwoMadeAllCells, onSelectionThreeMadeAllCells, onSelectionFourMadeAllCells, plotAllCells, allDataOutlierIndices }) {

    const timeOutId = useRef()

    const [text, setText] = useState([])
    const [allCellsDisplayText, setAllCellsDisplayText] = useState([])
    const [colors, setColors] = useState([])
    const [intensityRange, setIntensityRange] = useState([])

    const [dataOneAllCellsValuesLocal, setDataOneAllCellsValuesLocal] = useState(dataOneAllCellsValues)
    const [dataTwoAllCellsValuesLocal, setDataTwoAllCellsValuesLocal] = useState(dataTwoAllCellsValues)
    const [dataThreeAllCellsValuesLocal, setDataThreeAllCellsValuesLocal] = useState(dataThreeAllCellsValues)
    const [dataFourAllCellsValuesLocal, setDataFourAllCellsValuesLocal] = useState(dataFourAllCellsValues)


    const [pointFocused, setPointFocused] = useState(false)
    const [focusedColors, setFocusedColors] = useState([])
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

    const [hideOutliersChecked, setHideOutliersChecked] = useState(false)

    const [lastSegmentationIndex, setLastSegmentationIndex] = useState(0)

    const [dataFourDisplayValue, setDataFourDisplayValue] = useState(dataFourAllCellsValues[0])



    window.addEventListener('resize', () => onWindowUpdate())

    useEffect(() => {
        console.log(dataFourAllCellsValues)
        if (dataOne) {
            const formData = new FormData()
            formData.append('Project', project)
            formData.append('Date', date)

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
        setDataFourAllCellsValuesLocal(dataFourAllCellsValues)
    }, [dataOneAllCellsValues, dataTwoAllCellsValues, dataThreeAllCellsValues, dataFourAllCellsValues])

    useEffect(() => {
        const tempIntensityRange = []
        for (var i = 0; i < 256; i++) {
            tempIntensityRange[i] = i
        }
        setIntensityRange(tempIntensityRange)
    }, [])

    useEffect(() => {
        if (dataOne) {
            setText([dataOne, dataTwo, dataThree, dataFour])
        }
    }, [dataOne, dataTwo, dataThree, dataFour])

    useEffect(() => {
        if (dataOne) {
            const colorsTemp = []

            const maxDataFourValue = Math.max(...dataFourAllCellsValuesLocal) - Math.min(...dataFourAllCellsValuesLocal)

            for (var i = 0; i < dataFourAllCellsValuesLocal.length; i++) {
                const ratio = (dataFourAllCellsValuesLocal[i] - Math.min(...dataFourAllCellsValuesLocal)) / maxDataFourValue
                const blue = Math.round(255 * ratio)
                const red = Math.round(255 - (255 * ratio))
                colorsTemp[i] = `rgb(${red}, 0, ${blue})`;
            }

            console.log(colorsTemp)
            setColors(colorsTemp)
        }
    }, [dataFourAllCellsValuesLocal])

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

        const margin = `min(${2.5 + (divBlueValue * 0.1568627)}vw, ${70 + (divBlueValue * 2.5098)}px)`
        

        setFocusedColors(tempFocusedColors)
        setFocusedDateMargin(margin)
        setDataFourDisplayValue(dataFourAllCellsValuesLocal[closestIndex])
        setPointFocused(true)

    }

    const onMouseLeaveColorFrequency = () => {
        setPointFocused(false)
    }

    const handleLayoutChange = (e) => {
        setTempCamera(e['scene.camera'])
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

    const selectionFourMadeAllCells = (parameter) => {
        onSelectionFourMadeAllCells(parameter)
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
            setDataOneAllCellsValuesLocal(dataOneAllCellsValues.filter((value, index) => !allDataOutlierIndices.includes(index)))
            setDataTwoAllCellsValuesLocal(dataTwoAllCellsValues.filter((value, index) => !allDataOutlierIndices.includes(index)))
            setDataThreeAllCellsValuesLocal(dataThreeAllCellsValues.filter((value, index) => !allDataOutlierIndices.includes(index)))
            setDataFourAllCellsValuesLocal(dataFourAllCellsValues.filter((value, index) => !allDataOutlierIndices.includes(index)))
        } else {
            setDataOneAllCellsValuesLocal(dataOneAllCellsValues)
            setDataTwoAllCellsValuesLocal(dataTwoAllCellsValues)
            setDataThreeAllCellsValuesLocal(dataThreeAllCellsValues)
            setDataFourAllCellsValuesLocal(dataFourAllCellsValues)
        }
    }, [hideOutliersChecked, dataOne, dataTwo, dataThree, dataFour])

    const onDatapointHover = (e) => {
        if (e.points[0].text[4] != lastSegmentationIndex) {
            setLastSegmentationIndex(e.points[0].text[4])
            clearTimeout(timeOutId.current)
            timeOutId.current = setTimeout(() => {
                const point_text = e.points[0].text
                console.log(point_text)

                var formData = new FormData()
                formData.append('Project', project)
                formData.append('Date', date)
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
            tempText[i] = [dataOne, dataTwo, dataThree, dataFour, i]
        }
        setAllCellsDisplayText(tempText)
        
    }, [dataOne, dataTwo, dataThree, dataFour])


    if (dataOne) {
        if (display) {
            return (
                <div>
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
                                <div style={{fontSize: "min(0.9vw, 10px)"}}>{date}</div>
                            </div>
                            
                        </div>
                        <div>
                            <Plot 
                                data={
                                    [
                                        {
                                            x: dataOneAllCellsValuesLocal,
                                            y: dataTwoAllCellsValuesLocal,
                                            z: dataThreeAllCellsValuesLocal,
                                            //text: Array(dataOneAllCellsValues[index].length).fill(text[index]),
                                            text: allCellsDisplayText,
                                            hovertemplate: 
                                                '<br><b>%{text[0]}</b>: %{x:.2f}<br>' +
                                                '<b>%{text[1]}</b>: %{y:.2f}' +
                                                '<br><b>%{text[2]}</b>: %{z:.2f}<br>' +
                                                '<b>%{text[3]}</b>: %{z:.2f}',
                                            type: 'scatter3d',
                                            mode: 'markers',
                                            marker: {
                                                size: 2,
                                                color: (pointFocused) ? focusedColors : colors,
                                                opacity: 1
                                            },
                                            showlegend: false,
                                            name: ""
                                        }
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
                                    height: 'min(45vw, 750px)',
                                }}
                                onRelayout={(e) => handleLayoutChange(e)}
                                onClick={(e) => handleLayoutChange(e)}
                                onAfterPlot={() => setCurrentCamera(tempCamera)}
                                onHover={(e) => onDatapointHover(e)}
                            />
                            <div style={{width: 'min(50vw, 800px)', height: 'min(6vw, 80px)', backgroundColor: 'white'}}>
                            <div style={{fontSize: 'min(0.9vw, 10px)', marginLeft: focusedDateMargin, color: pointFocused ? 'black' : 'white'}}>{Math.round(dataFourDisplayValue * 100000) / 100000}</div>
                                <div style={{display: 'flex', marginLeft: 'min(5vw, 80px)', backgroundColor: 'black', height: 'min(2vw, 25px)', width: 'min(40vw, 640px)'}}>
                                    {intensityRange.map((num, index) => {
                                        return (
                                            <div onMouseEnter={() => get_closest_color(num)} onMouseLeave={() => onMouseLeaveColorFrequency()} style={{width: "min(0.1568627vw, 2.5098px)", height: "min(2vw, 25px)", backgroundColor: `rgb(${255 - num}, 0, ${num})`}}/>
                                        )
                                    })}
                                </div>
                                <div style={{display: 'flex', marginLeft: 'min(4vw, 40px)', width: '50vw', marginTop: '0.5vw'}}>
                                    <div style={{fontSize: 'min(1vw, 14px)'}}>{(Math.round(Math.min(...dataFourAllCellsValuesLocal) * 100000)) / 100000}</div>
                                    <div style={{fontSize: 'min(1vw, 14px)', marginLeft: 'min(35vw, 600px)'}}>{(Math.round(Math.max(...dataFourAllCellsValuesLocal) * 100000)) / 100000}</div>
                                </div>
                            </div>
                            <DropDownMenu 
                                numParameters={4}
                                onSelectionOneMade={selectionOneMadeAllCells}
                                onSelectionTwoMade={selectionTwoMadeAllCells}
                                onSelectionThreeMade={selectionThreeMadeAllCells}
                                onSelectionFourMade={selectionFourMadeAllCells}
                                parameterOne={dataOne}
                                parameterTwo={dataTwo}
                                parameterThree={dataThree}
                                parameterFour={dataFour}
                            />
                        </div>
                        
                    </div>
                </div>
            )
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

export default SingleImageCellPlot