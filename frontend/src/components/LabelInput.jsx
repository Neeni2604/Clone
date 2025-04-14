import PropTypes from "prop-types";

export default function LabelInput({ name, type, value, setValue }) {
    return (
        <div className="flex flex-col">
            <label htmlFor={name}>
                {name}
            </label>
            <input 
                id={name} 
                type={type}
                name={name} 
                placeholder={name}
                value={value} 
                onChange={(e) => setValue(e.target.value)}
            />
        </div>
    );
}

LabelInput.propTypes = {
    name: PropTypes.string,
    type: PropTypes.string,
    value: PropTypes.string,
    setValue: PropTypes.func,
}