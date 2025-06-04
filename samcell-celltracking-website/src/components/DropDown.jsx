import './DropDown.css'
import React, {useState, useEffect} from 'react';


const DropDown = ({ options, onDropDownSelection, axis, chosenParameter, small }) => {
    const [buttonText, setButtonText] = useState(chosenParameter);
    const [dropDownVisible, setDropDownVisible] = useState(false);
    const [selectedOptionIndex, setSelectedOptionIndex] = useState(-1);

    useEffect(() => {
        setButtonText(chosenParameter)
    }, [chosenParameter])

    const handleOnClick = () => {
        setDropDownVisible(!dropDownVisible);
    }

    const onSelection = (event, index) => {
        setSelectedOptionIndex(index);
        setButtonText(options[index]);
        onDropDownSelection(options[index]);
    }

    if (dropDownVisible) {
        return (
            <div className='drop_down_container' style={{marginLeft: (small) ? 'min(1.3vw, 20px)' : 'min(2.3vw, 41px)', marginRight: (small) ? 'min(1.3vw, 20px)' : 'min(2.3vw, 41px)'}}>
                <div style={{textAlign: 'center', fontSize: 'min(1.6vw, 24px)'}}>{axis}-Axis:</div>
                <button 
                    onClick={handleOnClick}
                    style={{
                        color: 'black', 
                        backgroundColor: 'rgb(232, 232, 232)', 
                        fontSize: 'min(1vw, 15px)', 
                        padding: 'min(0.6vw, 8px)', 
                        borderTopLeftRadius: '10px', 
                        borderTopRightRadius: '10px', 
                        borderColor: 'black', 
                        borderWidth: '2px', 
                        borderStyle: 'solid', 
                        width: (small) ? 'min(10vw, 154px)' : 'min(12vw, 185px)',
                    }}
                >
                    {buttonText}
                </button>
                <div className='options_box' style={{width: (small) ? 'min(10vw, 154px)' : 'min(12vw, 185px)',}}>
                    {options.map((optionText, index) => {
                        return (
                            <button
                                style={{
                                    color: (optionText == buttonText) ? 'white' : 'black', 
                                    backgroundColor: (optionText == buttonText) ? 'black' : 'white', 
                                    fontSize: 'min(1vw, 15px)', 
                                    padding: (small) ? 'min(2vw, 10px)' : 'min(4vw, 20px)', 
                                    borderColor: (optionText == buttonText) ? 'white' : 'black', 
                                    borderWidth: '1px', 
                                    borderStyle: 'solid', 
                                    width: (small) ? 'min(10vw, 154px)' : 'min(12vw, 185px)',
                                    opacity: 0.98,
                                    height: 'min(7.5vw, 100px)'
                                }}
                                onClick={e => onSelection(e, index)}
                            >
                                {optionText}
                            </button>
                        );
                    })}
                </div>
            </div>
        )
    } else {
        return (
            <div className='drop_down_container' style={{marginLeft: (small) ? 'min(1.3vw, 20px)' : 'min(2.3vw, 41px)', marginRight: (small) ? 'min(1.3vw, 20px)' : 'min(2.3vw, 41px)'}}>
                <div style={{textAlign: 'center', fontSize: 'min(1.6vw, 24px)'}}>{axis}-Axis:</div>
                <button 
                    onClick={handleOnClick}
                    style={{
                        color: 'black', 
                        backgroundColor: 'rgb(232, 232, 232)', 
                        fontSize: 'min(1vw, 15px)', 
                        padding: 'min(0.6vw, 8px)', 
                        borderRadius: '10px', 
                        borderColor: 'black', 
                        borderWidth: '2px', 
                        borderStyle: 'solid', 
                        width: (small) ? 'min(10vw, 154px)' : 'min(12vw, 185px)',
                    }}
                >
                    {buttonText}
                </button>
            </div>
        )
    }

    
}

export default DropDown;