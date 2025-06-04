import './TopBar.css'
import NavigationButton from './NavigationButton';

/**
 * TopBar Component containing header text and a page navigation button.
 *
 * @param {func} handleLayoutChange - Function to handle a navigation click
 * @param {string} topbarText - Title of the current page
 * @param {string} buttonText - Current text on the navigation button
 * @returns {React.JSX.Element} - The TopBar element.
 */
function TopBar({ handleNavigationClick, topBarText, buttonText }) {
    return (
        <div className="top_bar_container">
            <h1 className='top_bar_header_text'>{topBarText}</h1>
            <NavigationButton handleNavigationClick={handleNavigationClick} buttonText={buttonText} />
        </div>
    )
}

export default TopBar;