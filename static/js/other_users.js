const search = document.querySelector('#search')
const results = document.querySelector('#results')

class Node {
  constructor(value = ''){
    this.value = value;
    this.children = [];
    this.end = false;
  }
  setEnd() {
      this.end = true;
  }
  isEnd() {
      return this.end;
  }
}

class Trie {
  constructor() {
    this.root = new Node();
  }

   add(value, parent = this.root) {
    for (let i = 0; i < value.length; i++){
      // looks into all of the parents children and finds one that matches the current letter of the input word.
      let node = parent.children.find(child => child.value[i] === value[i])
      // if the node wasn't found, create one.
      if (!node) {
        node = new Node(value.slice(0, i+1));
        parent.children.push(node);
      }
      if (i === (value.length - 1)){
          node.setEnd()
      }
      parent = node
    }
   }
  // this.root = the root of the entire trie
  find(value, parent = this.root) {
      // loop through every letter in the value
    for (let i = 0; i < value.length; i++){
        //
      parent = parent.children.find(child => child.value[i] === value[i]);

      if (!parent){
          return null;
      }
    }
    return parent;
  }

  findWords(value, parent=this.root) {
    let top = this.find(value, parent)
    //if no matches are found, return nothing.
    if (!top) return [];

    // Else get all possible words for that value
    function getWords(node) {
        let words = [];
        if (node.isEnd()){
            words.push(node);
        }
        for (let child of node.children){
            words = [...words, ...getWords(child)]
        }
        return words;
    }
    return getWords(top)
  }
}

const trie = new Trie();

search.addEventListener('keyup', () => {

    // Returns an array of possible words.
    const nodes = trie.findWords(search.value.toLowerCase());

    console.log("NODES: ", nodes)

    //if no matching words were found in the trie:
    if (!nodes.length) return;

    all = document.querySelectorAll('.user-name')

    console.log("ALL: ", all)

    for (let elem of all){
        elem.classList.remove('show')
    }

    // Selects any element that has the same value as the nodes and displays them.

    for (let node of nodes) {
        // loop through each of the names in the allNames list.
        for (let name of all){
          console.log("TRIE NODE: ", node.value)
          console.log("NAME ID (username): ", name.id)
          console.log("FNAME: ", name.dataset.fname)
          console.log("LNAME: ", name.dataset.fname)
          if (
          node.value === name.id ||
          node.value === name.dataset.fname ||
          node.value === name.dataset.lname){
            console.log("Adding show class")
            name.classList.add('show')
          }
        }
        // results.innerHTML += `<li>${node.value}</li>`
        // let e = document.getElementById(`${node.value}`)
        // let fname = document.dataset.fname
        // let lname = document.dataset.lname
        // e.classList.add('show')
        // fname.classList.add('show')
        // lname.classList.add('show')



    }
})


function make_trie(users){
  for (let [username, fname, lname] of users){
    trie.add(username)
    trie.add(fname)
    trie.add(lname)
  } 
}

make_trie(users)