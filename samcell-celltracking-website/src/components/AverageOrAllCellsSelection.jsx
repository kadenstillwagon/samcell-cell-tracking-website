import './AverageOrAllCellsSelection.css'
import { useState } from 'react'

/**
 * AverageOrAllCellsSelection Component that allows user to select whethere they want to upload 
 * a single or multiple images to the project
 *
 * @param {func} onAverageClick - Function to handle a click on the average parameter button
 * @param {func} onAllCellsClick - Function to handle a click on the all cell's parameters button
 * @param {string} selectedButton - String specifying which button (average or all cells) is currently selected 
 * @returns {React.JSX.Element} - The AverageOrAllCellsSelection element.
 */
function AverageOrAllCellsSelection({ onAverageClick, onAllCellsClick, selectedButton }) {
    const [selected, setSelected] = useState(selectedButton)

    const handleOnAverageClick = () => {
        setSelected('Average')
        onAverageClick()
    }

    const handleOnAllCellsClick = () => {
        setSelected('All Cells')
        onAllCellsClick()
    }

    return (
        <div className='tl-ct-selection-container'>
            <button
                style={{
                    fontSize: 'min(1.6vw, 17px)', 
                    padding: 'min(1.1vw, 9px)', 
                    width: 'min(14vw, 150px)',
                    borderWidth: 0,
                    borderRadius: '15px',
                    backgroundColor: (selected == 'Average') ? 'rgb(63, 63, 163)' : 'white',
                    color: (selected == 'Average') ? 'white' : 'black'
                }}
                
                onClick={handleOnAverageClick}
                >
                Image Average
            </button>

            <button
                style={{
                    fontSize: 'min(1.6vw, 17px)', 
                    padding: 'min(1.1vw, 9px)', 
                    width: 'min(14vw, 150px)',
                    borderWidth: 0,
                    borderRadius: '15px',
                    backgroundColor: (selected == 'All Cells') ? 'rgb(63, 63, 163)' : 'white',
                    color: (selected == 'All Cells') ? 'white' : 'black'
                }}
                
                onClick={handleOnAllCellsClick}
                >
                All Cells
            </button>
        </div>
    )
}

export default AverageOrAllCellsSelection