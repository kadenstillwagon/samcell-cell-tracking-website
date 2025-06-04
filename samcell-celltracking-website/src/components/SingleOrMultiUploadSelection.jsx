import './SingleOrMultiUploadSelection.css'
import { useState } from 'react'

/**
 * SingleOrMultiUploadSelection Component that allows user to select whethere they want to upload 
 * a single or multiple images to the project
 *
 * @param {func} onSingleClick - Function to handle a click on the single image upload button
 * @param {func} onMultiClick - Function to handle a click on the multi image upload button
 * @param {string} selectedButton - String specifying which button (single or multi) is currently selected 
 * @returns {React.JSX.Element} - The SingleOrMultiUploadSelection element.
 */
function SingleOrMultiUploadSelection({ onSingleClick, onMultiClick, selectedButton }) {
    const [selected, setSelected] = useState(selectedButton)

    const handleOnSingleClick = () => {
        setSelected('Single')
        onSingleClick()
    }

    const handleOnMultiClick = () => {
        setSelected('Multi')
        onMultiClick()
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
                    backgroundColor: (selected == 'Single') ? 'rgb(63, 63, 163)' : 'white',
                    color: (selected == 'Single') ? 'white' : 'black'
                }}
                
                onClick={handleOnSingleClick}
                >
                Single Upload
            </button>

            <button
                style={{
                    fontSize: 'min(1.6vw, 17px)', 
                    padding: 'min(1.1vw, 9px)', 
                    width: 'min(14vw, 150px)',
                    borderWidth: 0,
                    borderRadius: '15px',
                    backgroundColor: (selected == 'Multi') ? 'rgb(63, 63, 163)' : 'white',
                    color: (selected == 'Multi') ? 'white' : 'black'
                }}
                
                onClick={handleOnMultiClick}
                >
                Multi Upload
            </button>
        </div>
    )
}

export default SingleOrMultiUploadSelection