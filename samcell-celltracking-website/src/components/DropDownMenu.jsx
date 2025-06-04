import DropDown from './DropDown';
import React, {useState} from 'react'

const DropDownMenu = ({ numParameters, onSelectionOneMade, onSelectionTwoMade, onSelectionThreeMade, onSelectionFourMade, parameterOne, parameterTwo, parameterThree, parameterFour }) => {

    const options = [
        'Principal Component 1',
        'Principal Component 2',
        'Principal Component 3',
        'Perimeter',
        'Area',
        'Convex Hull Area',
        'Convex Hull Perimeter',
        'Min Bounding Radius',
        'Max Bounding Radius',
        'Number of Surrounding Cells',
        'Spikiness',
        'Elongation',
        'Compactness (1)',
        'Compactness (2)',
        'Circularity (1)',
        'Circularity (2)',
        'Circularity (3)',
        'Circularity (4)',
        'Convexity (1)',
        'Convexity (2)',
        'Roughness (1)',
        'Roughness (2)',
        'Roughness (3)',
        'Mean Radial Distance',
        'Mean Radial Distance Crossings',
        'STD Radial Distance',
        'Entropy of Radial Distance',
        'Mean Intensity',
        'STD_Intensity',
        'Max Intensity',
        'Min Intensity',
        'Intensity Range',
        'Intensity Gradient Metric',
        'Haralick - Angular Second Moment (Direction 1)',
        'Haralick - Contrast (Direction 1)',
        'Haralick - Correlation (Direction 1)',
        'Haralick - Sum of Squares: Variance (Direction 1)',
        'Haralick - Inverse Difference Moment (Direction 1)',
        'Haralick - Sum Average (Direction 1)',
        'Haralick - Sum Variance (Direction 1)',
        'Haralick - Sum Entropy (Direction 1)',
        'Haralick - Entropy (Direction 1)',
        'Haralick - Difference Variance (Direction 1)',
        'Haralick - Difference Entropy (Direction 1)',
        'Haralick - Information Measure Correlation 1 (Direction 1)',
        'Haralick - Information Measure Correlation 2 (Direction 1)',
        'Haralick - Maximal Correlation Coefficient (Direction 1)',
        'Haralick - Angular Second Moment (Direction 2)',
        'Haralick - Contrast (Direction 2)',
        'Haralick - Correlation (Direction 2)',
        'Haralick - Sum of Squares: Variance (Direction 2)',
        'Haralick - Inverse Difference Moment (Direction 2)',
        'Haralick - Sum Average (Direction 2)',
        'Haralick - Sum Variance (Direction 2)',
        'Haralick - Sum Entropy (Direction 2)',
        'Haralick - Entropy (Direction 2)',
        'Haralick - Difference Variance (Direction 2)',
        'Haralick - Difference Entropy (Direction 2)',
        'Haralick - Information Measure Correlation 1 (Direction 2)',
        'Haralick - Information Measure Correlation 2 (Direction 2)',
        'Haralick - Maximal Correlation Coefficient (Direction 2)',
        'Haralick - Angular Second Moment (Direction 3)',
        'Haralick - Contrast (Direction 3)',
        'Haralick - Correlation (Direction 3)',
        'Haralick - Sum of Squares: Variance (Direction 3)',
        'Haralick - Inverse Difference Moment (Direction 3)',
        'Haralick - Sum Average (Direction 3)',
        'Haralick - Sum Variance (Direction 3)',
        'Haralick - Sum Entropy (Direction 3)',
        'Haralick - Entropy (Direction 3)',
        'Haralick - Difference Variance (Direction 3)',
        'Haralick - Difference Entropy (Direction 3)',
        'Haralick - Information Measure Correlation 1 (Direction 3)',
        'Haralick - Information Measure Correlation 2 (Direction 3)',
        'Haralick - Maximal Correlation Coefficient (Direction 3)',
        'Haralick - Angular Second Moment (Direction 4)',
        'Haralick - Contrast (Direction 4)',
        'Haralick - Correlation (Direction 4)',
        'Haralick - Sum of Squares: Variance (Direction 4)',
        'Haralick - Inverse Difference Moment (Direction 4)',
        'Haralick - Sum Average (Direction 4)',
        'Haralick - Sum Variance (Direction 4)',
        'Haralick - Sum Entropy (Direction 4)',
        'Haralick - Entropy (Direction 4)',
        'Haralick - Difference Variance (Direction 4)',
        'Haralick - Difference Entropy (Direction 4)',
        'Haralick - Information Measure Correlation 1 (Direction 4)',
        'Haralick - Information Measure Correlation 2 (Direction 4)',
        'Haralick - Maximal Correlation Coefficient (Direction 4)',
        'Haralick - Angular Second Moment (Mean)',
        'Haralick - Contrast (Mean)',
        'Haralick - Correlation (Mean)',
        'Haralick - Sum of Squares: Variance (Mean)',
        'Haralick - Inverse Difference Moment (Mean)',
        'Haralick - Sum Average (Mean)',
        'Haralick - Sum Variance (Mean)',
        'Haralick - Sum Entropy (Mean)',
        'Haralick - Entropy (Mean)',
        'Haralick - Difference Variance (Mean)',
        'Haralick - Difference Entropy (Mean)',
        'Haralick - Information Measure Correlation 1 (Mean)',
        'Haralick - Information Measure Correlation 2 (Mean)',
        'Haralick - Maximal Correlation Coefficient (Mean)',
    ]

    if (numParameters == 3) {
        return (
            <div >
                <div style={{display: "flex", width: "min(50vw, 800px)", backgroundColor: 'white', height: 'min(7.5vw, 116px'}}>
                    <DropDown options={options} onDropDownSelection={onSelectionOneMade} axis={"X"} chosenParameter={parameterOne} small={false}/>
                    <DropDown options={options} onDropDownSelection={onSelectionTwoMade} axis={"Y"} chosenParameter={parameterTwo} small={false}/>
                    <DropDown options={options} onDropDownSelection={onSelectionThreeMade} axis={"Z"} chosenParameter={parameterThree} small={false}/>
                </div>
            </div>
        )
    } else {
        return (
            <div >
                <div style={{display: "flex", width: "min(50vw, 800px)", backgroundColor: 'white', height: 'min(11vw, 150px', justifyContent: 'center'}}>
                    <DropDown options={options} onDropDownSelection={onSelectionOneMade} axis={"X"} chosenParameter={parameterOne} small={true}/>
                    <DropDown options={options} onDropDownSelection={onSelectionTwoMade} axis={"Y"} chosenParameter={parameterTwo} small={true}/>
                    <DropDown options={options} onDropDownSelection={onSelectionThreeMade} axis={"Z"} chosenParameter={parameterThree} small={true}/>
                    <DropDown options={options} onDropDownSelection={onSelectionFourMade} axis={"Color"} chosenParameter={parameterFour} small={true}/>
                </div>
            </div>
        )
    }
    
}

export default DropDownMenu;