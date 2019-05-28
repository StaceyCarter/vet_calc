function Divisions(props){

  let display = (props.drugForm === "liq")? 'hide' : '';

  return (
    <div className={display}>
      <label>
        How many pieces can your tablets be divided into?
        <input type="number" value={props.divisions} onChange={(evt) => props.setDivisions(evt.target.value)} /> pieces
      </label>
    </div>
  )
}