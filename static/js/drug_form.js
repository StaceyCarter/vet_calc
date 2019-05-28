class LiqOrTabs extends React.Component {
  constructor(props){
    super(props);

    this.state = {
      drugForm : "liq"
    }

    this.changeForm = this.changeForm.bind(this)
  }

  changeForm(evt) {
    this.setState({
      drugForm : evt.target.value
    },
    () => this.props.setForm(this.state.drugForm))
  }

  render () {
  return (
      <div>
        <label>
          <input
            type="radio"
            value="liq"
            checked={this.state.drugForm === "liq"}
            onChange={this.changeForm}
            /> Liquid
        </label>
        <label>
          <input
            type="radio"
            value="tab"
            checked={this.state.drugForm === "tab"}
            onChange={this.changeForm}
            /> Tablet
        </label>
      </div>
    )
  }
}