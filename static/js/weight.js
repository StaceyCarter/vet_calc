

class KgOrLbs extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedOption: "kg"
    };

    this.handleOptionChange = this.handleOptionChange.bind(this);
  }

  handleOptionChange(evt) {
    this.setState({
      selectedOption: evt.target.value
    },
    () => this.props.changeUnit(this.state.selectedOption));
  }

  render() {
    return (
      <div className="weight-selector">
        <label>
          <input
            type="radio"
            value="kg"
            checked={this.state.selectedOption==="kg"}
            onChange={this.handleOptionChange}
          />
          kg
        </label>
        <label>
          <input
            type="radio"
            value="lbs"
            checked={this.state.selectedOption==="lbs"}
            onChange={this.handleOptionChange}
          />
          lbs
        </label>
      </div>
    );
  }
}

// Renders a weight input form and sets weight state in Form.
class Weight extends React.Component {
  constructor(props) {
    super(props);

    this.setWeightFromEvent = this.setWeightFromEvent.bind(this);
  }
// Sets the state as the new weight. If the input is NaN converts it to an empty string.
  setWeightFromEvent(e) {
    const value = parseFloat(e.target.value)
    const newValue = (Number.isNaN(value))? "" : value;
    this.props.setWeight(newValue)
  }

  render() {
    return (
      <div>
        <label>
          Weight:
          <input
            type="number"
            name="weight"
            step="0.01"
            value={this.props.weight}
            onChange={this.setWeightFromEvent}
            required
          />
        </label>
      </div>
    );
  }
}