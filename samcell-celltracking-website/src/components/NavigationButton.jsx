import './NavigationButton.css'

function NavigationButton({ handleNavigationClick, buttonText }) {

    const handleOnClick = () => {
        handleNavigationClick();
    }

    return (
        <button className="new_file_button" onClick={handleOnClick}>
            {buttonText}
        </button>
    )
}

export default NavigationButton