

function Route(props) {
  return (
    <div>
      <select>
        <option value="PO">PO</option>
        <option value="OU">OU</option>
        <option value="OD">OD</option>
        <option value="OS">OS</option>
        <option value="SQ">SQ</option>
        <option value="IM">IM</option>
      </select>
    </div>
  )
}


function Frequency(props){
  return(
    <div>
      <label>

      How often would you like to give it? q <input type="number" name="frequency" value="" readOnly />hrs
      </label>
    </div>
  )
}

function Duration(props){
  return(
    <div>
      <label>
      How long do you want to give it for? <input type="number" name="duration" value="" readOnly /> days
      </label>
    </div>
  )
}

function Label(props){
  return(
    <div>
      <label> Label: <br />
        <textarea readOnly></textarea>
      </label>
      <p> Form state info: </p>
      <ul>
        <li>Weight: {props.weight} {props.units}</li>
        <li>Weight in kg: {props.kgWeight}kg</li>
        <li>Drug form: {props.drugForm}</li>
        <li>Concentration: {props.concentration}</li>
        <li>Divisions: {props.divisions}</li>
      </ul>

    </div>
  )
}

class Form extends React.Component{
  constructor(props){
    super(props)

    this.state = {
      weight : 0,
      units : "kg",
      weightInKgs : 0,
      drugForm : "liq",
      concentration : 0,
      divisions : 1,
    }

    this.setWeight = this.setWeight.bind(this)
    this.changeUnit = this.changeUnit.bind(this)
    this.setWeightInKgs = this.setWeightInKgs.bind(this)
    this.setDrugForm = this.setDrugForm.bind(this)
    this.setConcentration = this.setConcentration.bind(this)
    this.setDivisions = this.setDivisions.bind(this)
  }
  // Responds to the form input (passed in as a prop) and updates the state accordingly.
  setWeight(weight){
    console.log("Weight from setWeight: ", weight)
    this.setState({
      weight : weight
    })
    this.setWeightInKgs(weight)
  }

  // Passed in as a prob to KgOrLbs which changes the unit state depending on which one the user has selected.
  changeUnit(newUnit) {
    this.setState({
      units: newUnit
    }, () => this.setWeightInKgs(this.state.weight));
  }

  // Checks what the current weight units are. If they are lbs, then converts the weight to kgs and updates the weight in kgs state.
  setWeightInKgs(weight){
    if (this.state.units === "lbs"){
      this.setState({
        weightInKgs : (weight * 0.45359237).toFixed(2)
      })
    } else {
      this.setState({
        weightInKgs : weight
      })
    }
  }

  setDrugForm(newForm){
    this.setState({
      drugForm : newForm
    })
  }

  setConcentration(newConcentration){
    this.setState({
      concentration : newConcentration
    })
  }

  setDivisions(newDivision){
    this.setState({
      divisions : newDivision
    })
  }

  render(){
    return (
    <div>
        <h1>Hello world</h1>
        <Weight weight={this.state.weight} setWeight={this.setWeight} />
        <KgOrLbs changeUnit={this.changeUnit}/>
        <LiqOrTabs setForm={this.setDrugForm}/>
        <Route />
        <Concentration
          drugForm={this.state.drugForm}
          setConcentration={this.setConcentration}
          concentration={this.state.concentration} />
        <Divisions
          divisions={this.state.divisions}
          setDivisions={this.setDivisions}
          drugForm={this.state.drugForm}/>
        <DosePicker />
        <Frequency />
        <Duration />
        <Label
          weight={this.state.weight}
          units={this.state.units}
          kgWeight={this.state.weightInKgs}
          drugForm = {this.state.drugForm}
          concentration = {this.state.concentration}
          divisions = {this.state.divisions}/>
     </div>
    )
  }
}



ReactDOM.render(
  <Form />,
  document.getElementById('root')
)