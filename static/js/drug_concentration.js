function Concentration(props){
  let describingWord
  let units

  if (props.drugForm === "liq"){
    describingWord = "concentration"
    units = "mg/ml"
  } else if (props.drugForm === "tab"){
    describingWord = "strength of the tablet"
    units = "mg"
  }

  return (
    <div>
      <label>What is the {describingWord}?
        <input type="number" step="0.01" onChange={(evt) => {
           props.setConcentration(evt.target.value)}} />
        {units}
      </label>
    </div>
  )
}