// This is for Label Input
import PropTypes from "prop-types";

export default function LabelInput({ name, type, value, setValue }) {
    return (
        <div className="flex flex-col space-y-1">
            <label htmlFor={name} className="text-sm font-medium text-gray-700">
                {name}
            </label>
            <input 
                id={name} 
                type={type}
                name={name} 
                placeholder={name}
                value={value} 
                onChange={(e) => setValue(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
        </div>
    );
}

LabelInput.propTypes = {
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    setValue: PropTypes.func.isRequired,
}